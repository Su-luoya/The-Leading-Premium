# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 11:31:58
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-04 20:27:24
"""MarketTypeData().df_market_type"""


import sys
from pathlib import Path

import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.modules.setting import Setting
from source.modules.tools import singleton


@singleton
class MarketType(object):
    def __init__(
        self,
        file_name: str = "market_type.csv",
        columns: list[str] = ["stock", "market_type"],
    ) -> None:
        self.df_market_type: pd.DataFrame = pd.read_csv(
            f"{Setting.basic_path}/{file_name}"
        )
        self.df_market_type.columns = columns
        # Convert data type
        self.df_market_type = self.df_market_type.astype(
            {"stock": int, "market_type": int}
        )


@singleton
class ListedDelistedDate(object):
    def __init__(
        self,
        file_name: str = "listed_delisted.csv",
        columns: list[str] = ["stock", "listed_date", "delisted_date"],
    ) -> None:
        self.df_listed = pd.read_csv(f"{Setting.basic_path}/{file_name}")
        self.df_listed.columns = columns
        # Convert data type
        self.df_listed["stock"] = self.df_listed["stock"].astype(int)
        self.df_listed["listed_date"] = pd.to_datetime(self.df_listed["listed_date"])
        self.df_listed["delisted_date"] = pd.to_datetime(
            self.df_listed["delisted_date"]
        )
        # # Fill nan values
        # self.df_listed["delisted_date"] = self.df_listed["delisted_date"].fillna(
        #     pd.Timestamp("now").floor("D")
        # )


@singleton
class IndustryClassification(object):
    def __init__(
        self,
        file_name: str = "industry_classification.csv",
        columns: list[str] = ["stock", "implement_date", "industry_code"],
    ) -> None:
        self.df_industry = pd.read_csv(f"{Setting.basic_path}/{file_name}")
        self.df_industry.columns = columns


if __name__ == "__main__":
    # df_market = MarketType(
    #     # file_name="market_type.csv", columns=["stock", "market_type"]
    # ).df_market_type
    # ic(df_market)
    df_listed = ListedDelistedDate().df_listed
    ic(df_listed)
