# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 21:06:44
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-12 18:59:03
"""
@singleton()
Window(period, df)
"""

import math
import sys
from pathlib import Path
from random import choice
from typing import Any, Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
from icecream import ic
from tabulate import tabulate
from termcolor import cprint

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))


def cp(content: Any, color: Optional[str] = None) -> None:
    """
    Print colorize text.
    --------

    Args:
    --------
        content (str): Anything you want to print.
        color (Optional[str]): \n
        Choose from ["grey", "red", "green", "yellow", "blue", "magenta", "cyan"]. \n
        Nothing passed in → Random Color.

    Usages:
    --------
        >>> cp("Anything you want to print.")
        >>> cp("Anything you want to print.", color="red")
    """
    color_list: list[str] = [
        "grey",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
    ]
    cprint(
        text=content,
        color=choice(color_list) if color not in color_list else color,
        attrs=["bold"],
    )


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


class TTest(object):
    """
    T-Test (Applying the Newey and West (1987) adjustment)
    --------

    Args:
    --------
        test_series (list[float | int] | pd.Series[float | int]): Test series.

    Usages:
    --------
        >>> result: dict[str, float] = TTest([0.1, 0.11, 0.02, -0.1, -0.11, -0.01]).result
        >>> {
        ... "t_value": result.tvalues[0],
        ... "p_value": result.pvalues[0],
        ... }
    """

    def __init__(self, test_series) -> None:
        self.test_series = test_series
        # Using the Bartlett kernel to calculate max lags
        self.max_lags: int = math.ceil(4 * ((len(test_series) / 100) ** (2 / 9)))
        # T-test (NW adjust)
        self.nw_adjust()

    def nw_adjust(self) -> None:
        """T-test (NW adjust)"""
        model = sm.OLS(self.test_series, np.ones_like(self.test_series))
        result = model.fit(
            cov_type="HAC", cov_kwds={"maxlags": self.max_lags}, weights="bartlett"
        )
        self.result: dict[str, str] = {
            "t_value": format(result.tvalues[0], ".4f"),
            "p_value": format(result.pvalues[0], ".4f"),
        }

    def __repr__(self) -> str:
        return str(
            tabulate(
                {
                    "t-value": [self.result["t_value"]],
                    "p-value": [self.result["p_value"]],
                },
                headers="keys",
                tablefmt="pretty",
            )
        )


if __name__ == "__main__":
    t_test = TTest([0.1, 0.11, 0.02, -0.1, -0.11, -0.01])
    ic(t_test)
