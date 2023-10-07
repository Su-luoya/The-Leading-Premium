# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-15 16:28:50
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-07 15:28:57
"""
Factor().lead_lag() \n
"""

import sys
from pathlib import Path
from time import time

import numpy as np
import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))

from source.data.macro import GDP
from source.lead_lag.sample import Samples
from source.modules.cache import Cache, cp
from source.modules.setting import Setting
from source.modules.structure import LLWindow


class LeadLag(object):
    def __init__(self, sample: LLWindow):
        self.sample: LLWindow = sample

    def factor(self):
        self.cal_diff()
        self.generate_shift_data()
        self.cal_corr()
        self.cal_ll()
        self.add_period_column()

    def cal_diff(self) -> None:
        """Calculates the difference of Cashflow and GDP"""
        cp(
            "Calculate difference of cashflow and gdp...",
            color="yellow",
        )
        for cashflow_column in Setting.cashflow_measures:
            self.sample.df_dict[cashflow_column][[cashflow_column, "GDP"]] = (
                self.sample.df_dict[cashflow_column]
                .groupby("industry_code")[[cashflow_column, "GDP"]]
                .diff()
            )
            self.sample.df_dict[cashflow_column] = self.sample.df_dict[
                cashflow_column
            ].dropna()

    def generate_shift_data(self):
        """Generate shift columns for cashflow"""
        cp(
            f"Generate {Setting.shift_period*2} shift columns for cashflow...",
            color="yellow",
        )
        self.corr_columns_dict: dict[str, list[str]] = {}
        for cash_column in Setting.cashflow_measures:
            corr_columns: list[str] = []
            # Name and generate shift data
            for shift_period in range(-Setting.shift_period, Setting.shift_period + 1):
                # Name shift columns
                corr_column: str = (
                    f"{cash_column}{f'({shift_period})' if shift_period!=0 else ''}"
                )
                corr_columns.append(corr_column)
                # Generate shift columns
                self.sample.df_dict[cash_column][corr_column] = (
                    self.sample.df_dict[cash_column]
                    .groupby("industry_code")[cash_column]
                    .shift(shift_period)
                )
            # Save shift columns
            self.corr_columns_dict[cash_column] = corr_columns

    def cal_corr(self) -> None:
        """Calculate cross-correlation of dimension 1+2J on a rolling window with T"""
        cp(
            f"Calculate cross-correlation of dimension {1+2*Setting.shift_period} on a rolling window with {Setting.window_period} periods...",
            color="yellow",
        )
        for cash_column in Setting.cashflow_measures:
            self.sample.df_dict[cash_column] = (
                self.sample.df_dict[cash_column]
                .drop(columns=["year", "quarter", "GDP"])
                .groupby("industry_code")
                .rolling(window=Setting.window_period)
                .corr(self.sample.df_dict[cash_column]["GDP"])
                .apply(np.abs)  # Take the absolute value of cross-correlation
                .reset_index()
                .dropna()
                .drop(columns="level_1")
            )

    def shift_name_to_period(self, column_name: str) -> int:
        """Convert shift name to period number"""
        return (
            int(column_name[column_name.find("(") + 1 : column_name.find(")")])
            if "(" in column_name
            else 0
        )

    def cal_ll_max(self, df_cash: pd.DataFrame, cash_columns: list[str]):
        """
        Maximum cross-correlation
        #& for self.cal_ll()
        """
        return (
            df_cash[cash_columns]
            .idxmax(axis=1)
            .map(lambda x: self.shift_name_to_period(x))
        )

    def cal_ll_average(self, df_cash: pd.DataFrame, cash_columns: list[str]):
        """
        Industry-level weighted average of leads and lags
        #& for self.cal_ll()
        """
        return sum(
            df_cash[cash_column] * self.shift_name_to_period(cash_column)
            for cash_column in cash_columns
        ) / df_cash[cash_columns].sum(axis=1)

    def cal_ll_industry(self, df_cash: pd.DataFrame, cash_columns: list[str]):
        """
        Cross-industry of leads and lags
        #& for self.cal_ll()
        """
        return sum(
            df_cash[cash_column]
            * self.shift_name_to_period(cash_column)
            / df_cash[cash_column].sum()
            for cash_column in cash_columns
        )

    def cal_ll(self) -> None:
        """
        Measuring leads and lags
        --------
        1. Maximum cross-correlation
        2. Industry-level weighted average of leads and lags
        3. Cross-industry of leads and lags
        """
        cp("Calculate leads and lags indicator...", color="yellow")
        for cash_column in Setting.cashflow_measures:
            df_cash: pd.DataFrame = self.sample.df_dict[cash_column]
            cash_columns: list[str] = self.corr_columns_dict[cash_column]
            # 1. Maximum cross-correlation
            self.sample.df_dict[cash_column][
                f"LL_max({cash_column})"
            ] = self.cal_ll_max(
                df_cash=df_cash,
                cash_columns=cash_columns,
            )
            # 2.Industry-level weighted average of leads and lags
            self.sample.df_dict[cash_column][
                f"LL_average({cash_column})"
            ] = self.cal_ll_average(
                df_cash=df_cash,
                cash_columns=cash_columns,
            )
            # 3.Cross-industry of leads and lags
            self.sample.df_dict[cash_column][
                f"LL_industry({cash_column})"
            ] = self.cal_ll_industry(
                df_cash=df_cash,
                cash_columns=cash_columns,
            )

    def add_period_column(self) -> None:
        """Add period column"""
        for cash_column in Setting.cashflow_measures:
            self.sample.df_dict[cash_column]["period"] = self.sample.period
            self.sample.df_dict[cash_column] = self.sample.df_dict[cash_column][
                [
                    "period",
                    "industry_code",
                    f"LL_max({cash_column})",
                    f"LL_average({cash_column})",
                    f"LL_industry({cash_column})",
                ]
            ]


class Factor(object):
    """Lead and Lag Factor"""

    @Cache(file_path=f"{Setting.cache_path}/lead_lag.csv", test=False)
    def lead_lag(self) -> pd.DataFrame:
        t_all: float = time()
        ll_list = []
        for sample in Samples():
            t: float = time()
            ic(sample)
            ll = LeadLag(sample=sample)
            ll.factor()
            df_ll = None
            for cashflow_column in Setting.cashflow_measures:
                if df_ll is None:
                    df_ll = ll.sample.df_dict[cashflow_column]
                else:
                    df_ll = pd.merge(
                        df_ll,
                        ll.sample.df_dict[cashflow_column],
                        on=["industry_code", "period"],
                        how="outer",
                    )
            ll_list.append(df_ll)
            cp(f"cost time:{time() - t:.4f}s", color="red")
        cp(f"all time:{time() - t_all:.4f}s", color="red")
        return pd.concat(ll_list)


class LLFactor(object):
    def __init__(self, cashflow=None, measure=None) -> None:
        if cashflow is not None and measure is not None:
            self.df_factor = (
                Factor()  # type:ignore
                .lead_lag()[
                    [
                        "period",
                        "industry_code",
                        f"{measure}({cashflow})",
                    ]
                ]
                .dropna()
            )
        else:
            raise ValueError("`cashflow` and `measure` must be not None")


if __name__ == "__main__":
    # samples = Samples()
    # ll = LeadLag(next(samples))
    # ll.factor()
    # ic(ll.sample.df_dict["EBITDA"])
    # ic(ll.corr_columns_dict)
    df_factor = LLFactor(cashflow="EBITDA", measure="LL_industry").df_factor
    ic(df_factor)
