# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 20:36:49
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-26 14:53:15


"""
1. operating income before depreciation and net of interest expenses, income taxes, and dividends
2. operating income
3. earnings
4. investment-based measures of fundamental cash flows (i.e., gross value of property, plant and equipment)
5. EBITDA: earnings before interest, tax, depreciation and amortization
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
        # TODO


if __name__ == "__main__":
    df_ebitda = EBITDA().df_ebitda
    ic(df_ebitda)
