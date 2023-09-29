# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 20:36:49
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-29 19:43:36
"""
df_cashflow = get_cashflow()
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
warnings.filterwarnings("ignore")
sys.path.append(str(Path.cwd()))
from source.modules.cache import Cache
from source.modules.setting import Setting
from source.modules.tools import singleton


def cal_diff(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Calculate difference for given columns in a DataFrame"""
    # Construct a copy of stock and year data
    df_range: pd.DataFrame = df[["stock", "year"]]
    df_range["start_year"] = df_range["year"]
    df_range["end_year"] = df_range["year"] + 1
    # Search for the start year and end year for stocks
    df_range = (
        df_range.groupby("stock")[["start_year", "end_year"]]
        .agg({"start_year": min, "end_year": max})
        .reset_index()
    )
    # Merge year-quarter time series of all stocks with the origin EBIT/EBITDA data
    df = pd.merge(
        df,
        pd.concat(
            # Construct year-quarter time series for all stocks
            df_range[["stock", "start_year", "end_year"]]
            .apply(
                lambda row: pd.DataFrame(
                    {
                        "stock": [row["stock"]]
                        * (row["end_year"] - row["start_year"])
                        * 5,
                        "year": list(
                            np.repeat(range(row["start_year"], row["end_year"]), 5)
                        ),
                        # Include `quarter=0`
                        "quarter": [0, 1, 2, 3, 4]
                        * (row["end_year"] - row["start_year"]),
                    }
                ),  # type: ignore
                axis=1,
            )
            .to_list()
        ),
        on=["stock", "year", "quarter"],
        how="outer",
    ).sort_values(by=["stock", "year", "quarter"])
    # Calculate difference of cashflow data
    df.loc[
        df["quarter"] == 0,
        columns,
    ] = 0
    df[columns] = df.groupby(["stock", "year"])[columns].diff()
    # Delete `quarter==0`
    return df[df["quarter"] != 0]


@singleton
class EBITDAData(object):
    """EBITDA and EBIT data"""

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
        cashflow_columns: list[str] = ["EBIT", "EBIT(TTM)", "EBITDA", "EBITDA(TTM)"]
        # Read EBITDA/EBIT data
        self.df_ebitda: pd.DataFrame = pd.read_csv(
            f"{Setting.cashflow_path}/{file_name}"
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
        self.df_ebitda = cal_diff(df=self.df_ebitda, columns=cashflow_columns)


@singleton
class IncomeData(object):
    """Income statement data"""

    def __init__(
        self,
        file_name: str = "income.csv",
        columns: list[str] = [
            "stock",
            "year",
            "quarter",
            "total_operating_income",
            "operating_income",
            "operating_profit",
            "total_profit",
            "net_profit",
        ],
    ) -> None:
        cashflow_columns: list[str] = [
            "total_operating_income",
            "operating_income",
            "operating_profit",
            "total_profit",
            "net_profit",
        ]
        # Read income data
        self.df_income: pd.DataFrame = pd.read_csv(
            f"{Setting.cashflow_path}/{file_name}"
        )
        # Set columns in order
        self.df_income.columns = columns
        # Convert data type
        self.df_income = self.df_income.astype(
            {
                "stock": int,
                "year": int,
                "quarter": int,
                "total_operating_income": float,
                "operating_income": float,
                "operating_profit": float,
                "total_profit": float,
                "net_profit": float,
            }
        )
        # Sort values
        self.df_income = self.df_income.sort_values(by=["stock", "year", "quarter"])
        # Set start year
        self.df_income = self.df_income[
            self.df_income["year"] >= Setting.sample_start_year
        ]
        # Calculate difference of income cashflow columns
        self.df_income = cal_diff(df=self.df_income, columns=cashflow_columns)


@singleton
class CashflowData(object):
    """Cashflow statement data"""

    def __init__(
        self,
        file_name: str = "cashflow.csv",
        columns: list[str] = [
            "stock",
            "year",
            "quarter",
            "operating_cashflow",
            "investing_cashflow",
            "financing_cashflow",
            "cash_increase",
        ],
    ) -> None:
        cashflow_columns: list[str] = [
            "operating_cashflow",
            "investing_cashflow",
            "financing_cashflow",
            "cash_increase",
        ]
        # Read income data
        self.df_cashflow: pd.DataFrame = pd.read_csv(
            f"{Setting.cashflow_path}/{file_name}"
        )
        # Set columns in order
        self.df_cashflow.columns = columns
        # Convert data type
        self.df_cashflow = self.df_cashflow.astype(
            {
                "stock": int,
                "year": int,
                "quarter": int,
                "operating_cashflow": float,
                "investing_cashflow": float,
                "financing_cashflow": float,
                "cash_increase": float,
            }
        )
        # Sort values
        self.df_cashflow = self.df_cashflow.sort_values(by=["stock", "year", "quarter"])
        # Set start year
        self.df_cashflow = self.df_cashflow[
            self.df_cashflow["year"] >= Setting.sample_start_year
        ]
        # Calculate difference of income cashflow columns
        self.df_cashflow = cal_diff(df=self.df_cashflow, columns=cashflow_columns)


@Cache(file_path=f"{Setting.cache_path}/cashflow.csv", test=False)
def get_cashflow() -> pd.DataFrame:
    """Different measures of cashflow"""
    return (
        EBITDAData()
        .df_ebitda.merge(
            IncomeData().df_income,
            on=["stock", "year", "quarter"],
            how="outer",
        )
        .merge(
            CashflowData().df_cashflow,
            on=["stock", "year", "quarter"],
            how="outer",
        )
    )


if __name__ == "__main__":
    df_cashflow = get_cashflow()
    ic(df_cashflow)
