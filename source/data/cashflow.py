# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 20:36:49
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-29 17:48:41


"""
1. operating income before depreciation and net of interest expenses, income taxes, and dividends
2. operating income
3. earnings
4. investment-based measures of fundamental cash flows (i.e., gross value of property, plant and equipment)
5. EBITDA: earnings before interest, tax, depreciation and amortization
"""

import sys
import warnings
from pathlib import Path

import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
warnings.filterwarnings("ignore")
sys.path.append(str(Path.cwd()))
from source.modules.setting import Setting
from source.modules.tools import singleton


@singleton
class EBITDA(object):
    def __init__(
        self,
        file_name: str = "EBIT_EBITDA.csv",
        columns: list[str] = [
            "stock",
            "year",
            "quarter",
            "EBIT",
            "EBIT(TTM)",
            "EBITDA",
            "EBITDA(TTM)",
        ],
    ) -> None:
        self.columns = ["EBIT", "EBIT(TTM)", "EBITDA", "EBITDA(TTM)"]
        # Read EBITDA/EBIT data
        self.df_ebitda: pd.DataFrame = pd.read_csv(
            f"{Setting.cashflow_path}/{file_name}"  # type: ignore
        )
        # Set columns in order
        self.df_ebitda.columns = columns
        # Convert data type
        self.df_ebitda = self.df_ebitda.astype(
            {
                "stock": int,
                "year": int,
                "quarter": int,
                "EBIT": float,
                "EBIT(TTM)": float,
                "EBITDA": float,
                "EBITDA(TTM)": float,
            }
        )
        # Sort values
        self.df_ebitda = self.df_ebitda.sort_values(by=["stock", "year", "quarter"])
        # Set start year
        self.df_ebitda = self.df_ebitda[
            self.df_ebitda["year"] >= Setting.sample_start_year
        ]
        # Calculate difference of EBIT & EBITDA
        self.diff()

    def diff(self) -> None:
        """Calculate difference of EBIT & EBITDA"""
        # Construct a copy of stock and year data
        df_range = self.df_ebitda[["stock", "year"]]
        df_range["start_year"] = df_range["year"]
        df_range["end_year"] = df_range["year"] + 1
        # Search for the start year and end year for stocks
        df_range = (
            df_range.groupby("stock")[["start_year", "end_year"]]
            .agg({"start_year": min, "end_year": max})
            .reset_index()
        )
        # Construct year-quarter time series for all stocks
        df_range = df_range[["stock", "start_year", "end_year"]].apply(
            lambda row: pd.DataFrame(
                {
                    "stock": [row["stock"]] * (row["end_year"] - row["start_year"]) * 5,
                    "year": list(range(row["start_year"], row["end_year"])) * 5,
                    # Conclude `quarter=0`
                    "quarter": [0, 1, 2, 3, 4] * (row["end_year"] - row["start_year"]),
                }
            ),  # type: ignore
            axis=1,
        )
        # Merge year-quarter time series of all stocks with the origin EBIT/EBITDA data
        self.df_ebitda = pd.merge(
            self.df_ebitda,
            pd.concat(df_range.to_list()),
            on=["stock", "year", "quarter"],
            how="outer",
        ).sort_values(by=["stock", "year", "quarter"])
        # Calculate difference of EBIT and EBITDA data
        self.df_ebitda.loc[
            self.df_ebitda["quarter"] == 0,
            self.columns,
        ] = 0
        self.df_ebitda[self.columns] = self.df_ebitda.groupby(["stock", "year"])[
            self.columns
        ].diff()
        # Delete `quarter==0`
        self.df_ebitda = self.df_ebitda[self.df_ebitda["quarter"] != 0]


if __name__ == "__main__":
    df_ebitda = EBITDA().df_ebitda
    # ic(df_ebitda)
