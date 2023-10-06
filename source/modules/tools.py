# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 21:06:44
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-06 14:33:36
"""
@singleton()
Window(period, df)
"""

import sys
from pathlib import Path

from icecream import ic
import pandas as pd

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.modules.setting import Setting


def singleton(cls):
    """
    A singleton pattern decorator for a class.
    ------
    This decorator function takes a class as input and returns a function \n
    that ensures only one instance of the class is created and returned.

    Args:
    ------
        cls: The class to be made into a singleton.

    Returns:
    ------
        The singleton instance of the class.

    Usages:
    ------
        ```python
        @singleton
        class MyClass:
            def __init__(self, arg1, arg2):
                self.arg1 = arg1
                self.arg2 = arg2

        instance1 = MyClass("value1", "value2")
        instance2 = MyClass("value3", "value4")

        print(instance1 is instance2)
        ```
    """

    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


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
    """window for a specific cashflow column"""

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
