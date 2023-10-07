# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-07 16:31:00
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-07 18:55:57


import sys
from pathlib import Path
from time import time

import numpy as np
import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.data.basic import get_industry_classification
from source.data.trade import StockReturn
from source.lead_lag.factor import Factor
from source.modules.cache import Cache, cp
from source.modules.setting import Setting


class TestSample(object):
    def __init__(
        self, is_shift=True, freq="Y", cashflow="EBITDA", measure="LL_average"
    ) -> None:
        self.is_shift = is_shift
        self.freq: str = freq
        self.ll_column: str = f"{measure}({cashflow})"
        self.df_ll = (
            Factor()
            .df_ll[  # type:ignore
                ["industry_code", "period", self.ll_column]
            ]
            .dropna(subset=self.ll_column)
        )
        self.industry_number = self.df_ll["industry_code"].nunique()
        self.shift_ll_period()
        # self.standardization()
        self.group()

    def shift_ll_period(self):
        shift_period: int = Setting.shift_rank_period if self.is_shift else 0
        if self.freq == "Q":
            self.df_ll["period"] = self.df_ll["period"].map(
                lambda x: pd.Period(x, freq="Q") + shift_period
            )
        elif self.freq == "Y":
            self.df_ll["period"] = self.df_ll["period"].map(
                lambda x: pd.Period(x, freq="Q")
            )
            self.df_ll[self.ll_column] = self.df_ll.groupby(
                [self.df_ll["period"].dt.year, self.df_ll["industry_code"]]
            )[self.ll_column].transform(lambda x: x.iloc[0])
            self.df_ll["period_new"] = self.df_ll["period"] + shift_period
            self.df_ll = self.df_ll[self.df_ll["period"] > self.df_ll["period"][1]]
            self.df_ll["period"] = self.df_ll["period_new"]
            self.df_ll = self.df_ll.drop(columns="period_new")

    def standardization(self):
        self.df_ll = (
            self.df_ll.set_index("industry_code")
            .groupby("period")[[self.ll_column]]
            .apply(lambda x: (x - x.mean()) / x.std())
            .reset_index()
        )

    def group_rule(self, rank):
        """Top `Setting.top_group_industry_number` leading (lagging) industries"""
        if rank <= Setting.lead_group_industry_number:
            return "lead"
        elif rank > self.industry_number - Setting.lag_group_industry_number:
            return "lag"
        else:
            return "mid"

    def group(self):
        """Make breakpoint to group stocks into 3 portfolios"""
        self.df_ll[self.ll_column] = (
            self.df_ll.groupby("period")[[self.ll_column]]
            .rank(ascending=False)
            .applymap(self.group_rule)
        )
        # Date type
        self.df_ll["year"] = self.df_ll["period"].dt.year
        self.df_ll["quarter"] = self.df_ll["period"].dt.quarter
        self.df_ll = self.df_ll.drop(columns="period")

    def portfolio_sample(self):
        return (
            pd.merge(
                self.df_ll,
                # Merge stock return
                pd.merge(
                    StockReturn().df_ret,
                    get_industry_classification(),  # type:ignore
                    on=["stock", "year", "quarter"],
                    how="inner",
                ),
                on=["industry_code", "year", "quarter"],
                how="inner",
            )
            .dropna()
            .sort_values(["stock", "year", "quarter", "month"])
            .drop(columns="industry_code")
            .set_index(["stock", "year", "quarter", "month"])
            # .reset_index()
            .rename(columns={self.ll_column: "portfolio"})
        )


if __name__ == "__main__":
    test_sample = TestSample(is_shift=True, freq="Q")
    df_ll = test_sample.portfolio_sample()
    ic(df_ll)
