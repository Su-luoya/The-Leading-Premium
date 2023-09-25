# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-09-25 21:03:07
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-25 21:50:44
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


if __name__ == "__main__":
    df_gdp = GDPData().df_gdp
    ic(df_gdp)
