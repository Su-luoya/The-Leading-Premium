# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 21:06:44
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-05 15:33:07


import sys
from pathlib import Path

from icecream import ic

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
    def __init__(self, period, df) -> None:
        self.period = period
        self.df = df

    def __repr__(self) -> str:
        return f"Period:{self.period}, Stock Number:{len(self.df['stock'].unique())}, Industry Number:{len(self.df['industry_code'].unique())}"
