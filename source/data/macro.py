# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 21:03:07
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-26 15:26:12
"""GDPData().df_gdp"""


import sys
from pathlib import Path

import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.modules.setting import Setting
from source.modules.tools import singleton


@singleton
class GDPData(object):
    """
    GDP data pre-processing
    ------

    Args:
    --------
        file_name (str): GDP data file's name.
        columns (List[str]): GDP data columns' name. \n
        Defaults to ["year", "quarter", "GDP", "GDP_1", "GDP_2", "GDP_3"].

    Usages:
    ------
        ```python
        import pandas as pd
        df_gdp: pd.DataFrame = GDPData(
            file_name = "gdp.csv",
            columns = ["year", "quarter", "GDP", "GDP_1", "GDP_2", "GDP_3"]
            ).df_gdp
        print(df_gdp)
        ```
    """

    def __init__(
        self,
        file_name: str = "GDP.csv",
        columns: list[str] = ["year", "quarter", "GDP", "GDP_1", "GDP_2", "GDP_3"],
    ) -> None:
        self.df_gdp: pd.DataFrame = pd.read_csv(f"{Setting.macro_path}/{file_name}")
        # Rename columns in order
        self.df_gdp.columns = columns
        # Convert data type
        self.df_gdp = self.df_gdp.astype(
            {
                "year": int,
                "quarter": int,
                "GDP": int,
                "GDP_1": int,
                "GDP_2": int,
                "GDP_3": int,
            }
        )
        # Set start year
        self.df_gdp = self.df_gdp[self.df_gdp["year"] >= Setting.sample_start_year]


class RFRData(object):
    """
    Risk-free rate data preprocess
    --------

    Args:
    --------
        file_name (str, optional): Risk-free rate data file name. Defaults to "rfr.csv".
        columns (list[str], optional): Risk-free rate data columns. \n
        Defaults to ["year", "month", "rfr"]

    Usages:
    --------
        ```python
        import pandas as pd
        df_rfr: pd.DataFrame = RFRData().df_rfr
        print(df_rfr)
        ```
    """

    def __init__(
        self, file_name: str = "rfr.csv", columns: list[str] = ["year", "month", "rfr"]
    ) -> None:
        # Read risk-free rate data
        self.df_rfr: pd.DataFrame = pd.read_csv(f"{Setting.macro_path}/{file_name}")
        # Reset columns
        self.df_rfr.columns = columns
        # Type convert
        self.df_rfr = self.df_rfr.astype({"year": int, "month": int, "rfr": float})


if __name__ == "__main__":
    # df_gdp = GDPData().df_gdp
    # ic(df_gdp)
    df_rfr = RFRData().df_rfr
    ic(df_rfr)
