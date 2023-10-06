# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-06 15:00:24
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-06 18:02:26


import sys
from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.data.macro import GDP, Inflation
# from source.lead_lag.sample import Samples


class AdjustFactory(object):
    def __init__(self, df_adjust: pd.DataFrame, adjust_column: str) -> None:
        self.adjust_column = adjust_column
        self.df_adjust: pd.DataFrame = df_adjust


class InflationAdjust(AdjustFactory):
    df_inflation: pd.DataFrame = Inflation().df_inflation

    def inflation_adjust(self) -> None:
        self.df_adjust = pd.merge(
            self.df_adjust, self.df_inflation, on=["year", "quarter"], how="left"
        ).dropna(subset="inflation")
        self.df_adjust[self.adjust_column] = (
            self.df_adjust[self.adjust_column] / self.df_adjust["inflation"]
        )
        self.df_adjust.drop(columns="inflation", inplace=True)


class SeasonalAdjust(AdjustFactory):
    def generate_quarter_dummies(self) -> None:
        self.df_adjust = self.df_adjust.join(
            pd.get_dummies(self.df_adjust["quarter"]).astype(int)
        )

    def cal_resid(self, df: pd.DataFrame):
        """OLS (dummy variable)"""
        return (
            sm.OLS(df[self.adjust_column], sm.add_constant(df[[1, 2, 3]])).fit().resid
            + df[self.adjust_column].mean()
        )

    def seasonal_adjust(self):
        self.generate_quarter_dummies()
        self.df_adjust[self.adjust_column] = self.cal_resid(df=self.df_adjust)
        self.df_adjust = self.df_adjust.drop(columns=[1, 2, 3, 4])


class Adjust(InflationAdjust, SeasonalAdjust):
    """Inflation and Seasonal Adjust"""

    @property
    def adjust_result(self):
        self.inflation_adjust()
        self.seasonal_adjust()
        return self.df_adjust


if __name__ == "__main__":
    df_gdp = GDP().df_gdp
    # samples = Samples()
    # sample = next(samples)
    # df_adjust = sample.df_dict["EBITDA"]
    # df_adjust = Adjust(df_adjust, "EBITDA").adjust_result
    df_adjust = Adjust(df_gdp, "GDP").adjust_result
    ic(df_adjust)
