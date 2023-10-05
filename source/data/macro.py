# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 21:03:07
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-05 14:28:21
"""
GDPData().df_gdp \n
RFRData().df_rfr \n
InflationData().df_inflation
"""


import sys
from pathlib import Path

import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.modules.setting import Setting
from source.modules.tools import singleton


@singleton
class GDP(object):
    """
    GDP: GDP_1, GDP_2, GDP_3 (quarterly)
    """

    def __init__(
        self,
        file_name: str = "GDP.csv",
        columns: list[str] = ["year", "quarter", "GDP", "GDP_1", "GDP_2", "GDP_3"],
    ) -> None:
        self.df_gdp: pd.DataFrame = pd.read_csv(f"{Setting.macro_path}/{file_name}")
        # Rename columns in order
        self.df_gdp.columns = columns
        # Convert data type
        self.df_gdp = self.df_gdp.astype(
            {
                "year": int,
                "quarter": int,
                "GDP": int,
                "GDP_1": int,
                "GDP_2": int,
                "GDP_3": int,
            }
        )
        # Set start year
        self.df_gdp = self.df_gdp[self.df_gdp["year"] >= Setting.sample_start_year]


@singleton
class RFR(object):
    """
    Risk-free rate (monthly)
    """

    def __init__(
        self, file_name: str = "rfr.csv", columns: list[str] = ["year", "month", "rfr"]
    ) -> None:
        self.df_rfr: pd.DataFrame = pd.read_csv(f"{Setting.macro_path}/{file_name}")
        self.df_rfr.columns = columns
        self.df_rfr = self.df_rfr.astype({"year": int, "month": int, "rfr": float})
        self.df_rfr = self.df_rfr[self.df_rfr["year"] >= Setting.sample_start_year]


@singleton
class Inflation(object):
    """
    Inflation rate: CPI and PPI (quarterly)
    """

    def __init__(
        self,
        file_name: str = "inflation.csv",
        columns: list[str] = ["year", "quarter", "CPI", "PPI"],
    ) -> None:
        self.df_inflation: pd.DataFrame = pd.read_csv(
            f"{Setting.macro_path}/{file_name}"
        )
        self.df_inflation.columns = columns
        self.df_inflation = self.df_inflation.astype(
            {
                "year": int,
                "quarter": int,
                "CPI": float,
                "PPI": float,
            }
        )
        self.df_inflation = self.df_inflation[
            self.df_inflation["year"] >= Setting.sample_start_year
        ]


if __name__ == "__main__":
    # df_gdp = GDP().df_gdp
    # ic(df_gdp)
    # df_rfr = RFR().df_rfr
    # ic(df_rfr)
    df_inflation = Inflation().df_inflation
    ic(df_inflation)
