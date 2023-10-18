# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-07 19:03:41
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-18 18:13:48


import sys
from pathlib import Path

import numpy as np
import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.analysis.sample import TestSample
from source.modules.tools import TTest


class UnivariatePortfolio(object):
    """
    Univariate portfolio analysis
    --------
    1. Calculate average value-weighted excess returns for each portfolios
    2. NW-adjusted t-test on return series of zero-cost portfolio
    3. Three of five factor model fit on return series of portfolios (including zero-cost portfolio)

    Args:
    --------
        df_test (pd.DataFrame): Test sample dataframe.
        columns should be named like ['stock', 'year', ('quarter'), 'month', 'portfolio', 'value', 'return']
    """

    def __init__(self, df_test):
        self.df_test: pd.DataFrame = df_test
        self.cal_average_weighted_return()

    def cal_average_weighted_return(self):
        # Calculate sum of value
        self.df_test: pd.DataFrame = pd.merge(
            self.df_test,
            self.df_test.groupby(["year", "month", "portfolio"])[["size"]]
            .sum()
            .rename(columns={"size": "size_sum"}),
            on=["year", "month", "portfolio"],
            how="inner",
        )
        # Calculate value-weighted return
        self.df_test["return"] = (
            self.df_test["return"] * self.df_test["size"] / self.df_test["size_sum"]
        )
        self.df_test = pd.pivot(
            self.df_test.groupby(["year", "month", "portfolio"])[["return"]]
            .sum()
            .reset_index(),
            index=["year", "month"],
            columns="portfolio",
            values="return",
        )  # .reset_index()
        self.df_test["lead-lag"] = self.df_test["lead"] - self.df_test["lag"]

    def t_test(self) -> pd.DataFrame:
        """NW-adjusted t-test on return series of zero-cost portfolio"""
        # T-test (NW_adjust)
        t_test: pd.DataFrame = (
            self.df_test.apply(lambda series: TTest(test_series=series).result)
            .reset_index()
            .set_index("portfolio")
            .rename(columns={0: "test_result"})
        )
        # Calculate average return
        t_test["average_return"] = self.df_test.mean()
        t_test["volatility"] = self.df_test.std()
        t_test["sharpe_ratio"] = t_test["average_return"] / t_test["volatility"]
        # Get t value and p value
        t_test["p_value"] = t_test["test_result"].map(lambda x: x["p_value"])
        t_test["t_value"] = t_test["test_result"].map(lambda x: x["t_value"])
        t_test = t_test.drop(columns=["test_result"]).reset_index()
        return t_test

    def cumulative_log_excess_returns(self) -> None:
        self.df_test = self.df_test.apply(lambda x: np.log(x + 1))
        mean: float = self.df_test["lead-lag"].mean()
        std: float = self.df_test["lead-lag"].std()
        sharpe: float = (mean / std) * 12 ** (1 / 2)
        df_cum: pd.DataFrame = self.df_test.cumsum()
        ic(mean, std, sharpe, df_cum)


if __name__ == "__main__":
    up = UnivariatePortfolio(
        df_test=TestSample(
            is_shift=True,
            freq="Q",
            cashflow="EBITDA",
            measure="LL_average",
        )
        .portfolio_sample()
        .drop(columns=["quarter"])
    )
    t_test = up.t_test()
    up.cumulative_log_excess_returns()
    ic(t_test)
