# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 21:03:07
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-28 19:00:22
"""
GDPData().df_gdp
RFRData().df_rfr
InflationData().df_inflation
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

@singleton
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
        # Set start year
        self.df_rfr = self.df_rfr[self.df_rfr["year"] >= Setting.sample_start_year]

@singleton
class InflationData(object):
    """
    Inflation data preprocess
    ------

    Args:
    --------
        file_name (str, optional): Inflation data file name. Defaults to "inflation.csv".
        columns (list[str], optional): Inflation data columns. \n
        Defaults to ["year", "quarter", "CPI", "PPI"]

    Usages:
    --------
        ```python
        import pandas as pd
        df_inflation: pd.DataFrame = InflationData().df_inflation
        print(df_inflation)
        ```
    """

    def __init__(
        self,
        file_name: str = "inflation.csv",
        columns: list[str] = ["year", "quarter", "CPI", "PPI"],
    ) -> None:
        # Import CPI & PPI data
        self.df_inflation: pd.DataFrame = pd.read_csv(
            f"{Setting.macro_path}/{file_name}"
        )
        # Reset columns
        self.df_inflation.columns = columns
        # Convert data type
        self.df_inflation = self.df_inflation.astype(
            {
                "year": int,
                "quarter": int,
                "CPI": float,
                "PPI": float,
            }
        )
        # Set start year
        self.df_inflation = self.df_inflation[
            self.df_inflation["year"] >= Setting.sample_start_year
        ]


if __name__ == "__main__":
    # df_gdp = GDPData().df_gdp
    # ic(df_gdp)
    # df_rfr = RFRData().df_rfr
    # ic(df_rfr)
    df_inflation = InflationData().df_inflation
    ic(df_inflation)
