# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 11:31:58
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-25 20:05:35
"""MarketTypeData().df_market_type"""


import sys
from pathlib import Path

import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.modules.setting import Setting


class MarketTypeData(object):
    """
    Market type data
    --------

    Args:
    --------
        file_name (str): file name of market type data. Default to "market_type.csv".
        columns (List[str]): Columns in order. Defaults to ["stock", "market_type"].

    Usages:
    --------
        >>> import pandas as pd
        >>> df_market_type: pd.DataFrame = MarketTypeData().df_market_type
        >>> print(df_market_type)
    """

    __instance = None
    __first_init = True

    def __new__(
        cls,
        file_name: str = "market_type.csv",
        columns: list[str] = ["stock", "market_type"],
    ):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(
        self,
        file_name: str = "market_type.csv",
        columns: list[str] = ["stock", "market_type"],
    ) -> None:
        # Singleton mode
        if self.__first_init:
            # Read market type data file
            self.df_market_type: pd.DataFrame = pd.read_csv(
                f"{Setting.basic_path}/{file_name}"
            )
            # Rename columns in order
            self.df_market_type.columns = columns
            # Convert data type
            self.df_market_type = self.df_market_type.astype(
                {"stock": int, "market_type": int}
            )
            # Change the "__first_init" flag to False
            self.__first_init = False


if __name__ == "__main__":
    df_market = MarketTypeData(
        # file_name="market_type.csv", columns=["stock", "market_type"]
    ).df_market_type
    ic(df_market)
