# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-04 21:21:31
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-06 14:54:35
"""
Sample().get_samples()
Delete(window=next(samples)).cashflow_window
"""

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.data.basic import (
    AnnotationDate,
    ListedDelistedDate,
    MarketType,
    get_industry_classification,
)
from source.data.cashflow import get_cashflow
from source.modules.cache import Cache, cp
from source.modules.setting import Setting
from source.modules.tools import CashflowWindow, Window, singleton


@singleton
class Sample(object):
    """
    Generator for (20+4*2+1)-quarters-window of a sample period
    """

    def __init__(self) -> None:
        # Merge cashflow data and industry classification data
        self.df_cash = pd.merge(
            get_cashflow(),  # type: ignore
            get_industry_classification(),  # type: ignore
            on=["stock", "year", "quarter"],
            how="inner",
        )
        # Generate year_quarter column
        self.df_cash["year_quarter"] = self.df_cash[["year", "quarter"]].apply(
            lambda row: pd.Period(year=row["year"], quarter=row["quarter"], freq="Q"),
            axis=1,
        )
        # Generate period range
        self.period_range: np.ndarray[pd.Period, Any] = self.df_cash[
            "year_quarter"
        ].unique()

    def get_samples(self):
        """
        Sample Generator
        ------

        Returns:
        ------
            >>> {"quarter" : Period('2010Q1', 'Q-DEC'), "df_cash" : pd.DataFrame},
            >>> {"quarter" : Period('2010Q1', 'Q-DEC'), "df_cash" : pd.DataFrame},
            >>> ...
        """
        for period_index in filter(
            lambda x: len(x) >= Setting.sample_periods,
            [
                self.period_range[i : i + Setting.sample_periods]
                for i in range(len(self.period_range))
            ],
        ):
            yield Window(
                period=period_index[-1],
                df=self.df_cash[self.df_cash["year_quarter"].isin(period_index)].drop(
                    columns="year_quarter"
                ),
            )


class Delete(object):
    """
    Delete data that does not meet requirements
    ------
    1. Delete market type not in [1, 4]
    2. Delete stocks with delayed release of cashflow data
    3. Delete stocks that contain nan cashflow data and non industry classification data

    Usages
    ------
    ```python
    samples = Sample().get_samples()
    cashflow_window = Delete(window=next(samples)).cashflow_window
    ```
    """

    df_market_type: pd.DataFrame = MarketType().df_market_type
    df_listed: pd.DataFrame = ListedDelistedDate().df_listed
    df_anno: pd.DataFrame = AnnotationDate().df_anno

    def __init__(self, window: Window) -> None:
        self.window: Window = window
        self.delete_market()
        self.delete_delay()
        self.delete_unlisted()
        self.delete_nan()
        self.delete_unbalanced_stock()
        # ic(self.cashflow_window)

    def delete_market(self) -> None:
        """
        Delete market type not in [1, 4] \n
        1=上证A股市场 (不包含科创板），4=深证A股市场（不包含创业板）
        """
        cp(
            f"Delete market type not in {Setting.market_list}...",
            color="magenta",
        )
        # Merge market_type data
        self.window.df = pd.merge(
            self.window.df, self.df_market_type, on="stock", how="left"
        )
        # Delete market_type not in [1, 4]
        self.window.df = self.window.df[
            self.window.df["market_type"].isin(Setting.market_list)
        ].drop(columns="market_type")

    def delete_delay(self) -> None:
        """Delete stocks that have delayed release of financial data"""
        cp(
            "Delete stocks that have delayed release of financial data...",
            color="magenta",
        )
        # Merge annotation date data
        self.window.df = pd.merge(
            self.window.df, self.df_anno, on=["stock", "year", "quarter"], how="left"
        )
        # Delete delay data
        self.window.df = self.window.df[
            ~(
                self.window.df["annotation_date"]
                > (self.window.period + Setting.delay_max_period).end_time
            )
        ].drop(columns="annotation_date")

    def delete_unlisted(self) -> None:
        """
        Delete unlisted stocks' data
        --------
        Only stocks that are not unlisted at the end of the quarter are kept.
        """
        cp(
            "Delete unlisted stocks' data...",
            color="magenta",
        )
        # Merge cashflow data and unlisted date data
        self.window.df = pd.merge(
            self.window.df,
            self.df_listed.drop(columns=["listed_date", "delisted_date"]),
            on="stock",
            how="left",
        )
        # Delete unlisted stocks' data
        self.window.df = self.window.df[
            self.window.df.apply(
                lambda row: pd.Period(
                    year=row["year"], quarter=row["quarter"], freq="Q"
                ),
                axis=1,
            )
            > self.window.df["listed_year_quarter"]
        ]

    def delete_nan(self) -> None:
        """
        Delete stocks that contain nan cashflow data and non industry classification data
        """
        cp(
            "Delete stocks that contain nan cashflow data and non industry classification data...",
            color="magenta",
        )
        self.cashflow_window = CashflowWindow(self.window, Setting.cashflow_measures)
        del self.window
        for cashflow_column in self.cashflow_window.cashflow_columns:
            self.cashflow_window.window[cashflow_column] = (
                self.cashflow_window.window[cashflow_column]
                .groupby("stock")
                .filter(
                    lambda df: df[cashflow_column].notnull().all()
                    & df["industry_code"].notnull().all()
                )
            )

    def delete_unbalanced_stock(self):
        """Delete stocks that are not balanced during the window period"""
        if Setting.is_balance_panel:
            cp(
                "Delete stocks that are not balanced during the window period",
                color="magenta",
            )
            for cashflow_column in self.cashflow_window.cashflow_columns:
                self.cashflow_window.window[cashflow_column] = (
                    self.cashflow_window.window[cashflow_column]
                    .groupby("stock")
                    .filter(lambda df: len(df) < Setting.sample_periods)
                )


if __name__ == "__main__":
    samples = Sample().get_samples()
    # window1 = next(samples)
    # window2 = next(samples)
    # ic(type(window1.period))
    # ic(window2.period)
    # for sample in samples:
    #     ic(sample)
    cashflow_window = Delete(window=next(samples)).cashflow_window
    # for sample in samples:
    #     cashflow_window = Delete(window=sample).cashflow_window
    #     ic(cashflow_window)
    # delete = Delete(window=next(samples))
    # ic(delete.window)
