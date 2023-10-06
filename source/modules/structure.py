# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-06 19:05:00
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-06 19:14:21


import sys
from pathlib import Path

from icecream import ic
import pandas as pd

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.modules.setting import Setting
from source.lead_lag.adjust import Adjust


class Window(object):
    """
    (20+4*2+1)-quarters-window for a sample period
    ------

    Args:
    ------
        period: The sample period.
        df: The cashflow data.
    """

    def __init__(self, period: pd.Period, df: pd.DataFrame) -> None:
        self.period: pd.Period = period
        self.df: pd.DataFrame = df

    def __repr__(self) -> str:
        return str(
            {
                str(self.period): {
                    "Observation": len(self.df),
                    "Stock": len(self.df["stock"].unique()),
                    "Industry": len(self.df["industry_code"].unique()),
                }
            }
        )


class CashflowWindow(object):
    """Window for a specific cashflow column"""

    def __init__(self, window: Window, cashflow_columns: list[str]) -> None:
        self.cashflow_columns: list[str] = cashflow_columns
        self.period = window.period
        self.window: dict[str, pd.DataFrame] = {}
        for cashflow_column in self.cashflow_columns:
            self.window[cashflow_column] = window.df[
                ["stock", "year", "quarter", "industry_code", cashflow_column]
            ]

    def __repr__(self):
        return f"Window: {self.period}\n" + str(
            pd.DataFrame(
                {
                    cashflow_column: [
                        len(df),
                        len(df["stock"].unique()),
                        len(df["industry_code"].unique()),
                    ]
                    for cashflow_column, df in self.window.items()
                },
                index=["Observation", "Stock", "Industry"],
            ).T
        )
        

class LLWindow(object):
    """
    ```python
    ll_window = LLWindow(cashflow_window, df_gdp)
    ll_window.period
    ll_window.df_dict
    ```
    """

    def __init__(self, cashflow_window: CashflowWindow, df_gdp: pd.DataFrame):
        self.period: pd.Period = cashflow_window.period
        self.cashflow_columns = cashflow_window.cashflow_columns
        self.df_dict: dict[str, pd.DataFrame] = {
            cashflow_column: pd.merge(
                Adjust(
                    df_adjust=df_cash.drop(columns=["stock"])
                    .groupby(["industry_code", "year", "quarter"])
                    .sum()
                    .reset_index(),
                    adjust_column=cashflow_column,
                ).adjust_result,
                Adjust(df_adjust=df_gdp, adjust_column="GDP").adjust_result,
                on=["year", "quarter"],
                how="inner",
            )
            for cashflow_column, df_cash in cashflow_window.window.items()
        }

    def __repr__(self):
        return f"Window: {self.period}\n" + str(
            pd.DataFrame(
                {
                    cashflow_column: [
                        len(df),
                        len(df["industry_code"].unique()),
                    ]
                    for cashflow_column, df in self.df_dict.items()
                },
                index=["Observation", "Industry"],
            ).T
        )