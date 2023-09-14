"""MarketTypeData().df_market_type"""

import os
import sys

import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")

sys.path.append(os.path.dirname(__file__) + os.sep + "../")
from modules.setting import Setting


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
    __first_init = False

    def __new__(cls, file_name, columns):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(
        self,
        file_name: str = "market_type.csv",
        columns: list[str] = ["stock", "market_type"],
    ) -> None:
        if not self.__first_init:  # Singleton mode
            # Read market type data file
            self.df_market_type: pd.DataFrame = pd.read_csv(
                f"{Setting.cache_dir}/{Setting.basic_info_dir}/{file_name}"
            )
            # Rename columns in order
            self.df_market_type.columns = columns
            # Convert data type
            self.df_market_type = self.df_market_type.astype(
                {"stock": int, "market_type": int}
            )


if __name__ == "__main__":
    ic(
        MarketTypeData(
            file_name="market_type.csv", columns=["stock", "market_type"]
        ).df_market_type
    )
