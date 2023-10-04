# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 11:31:58
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-04 21:49:14
"""
MarketTypeData().df_market_type
ListedDelistedDate().df_listed
df_industry = get_industry_classification()
"""


import sys
from pathlib import Path

import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.modules.cache import Cache
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


@singleton
class IndustryClassification(object):
    def __init__(
        self,
        file_name: str = "industry_classification.csv",
        columns: list[str] = ["stock", "implement_date", "industry_code"],
    ) -> None:
        # Get industry classification
        self.df_industry = pd.read_csv(f"{Setting.basic_path}/{file_name}")
        self.df_industry.columns = columns
        self.df_industry["implement_date"] = pd.to_datetime(
            self.df_industry["implement_date"]
        )
        self.df_industry = self.df_industry.astype({"stock": int, "industry_code": int})
        # Get delisted date
        self.delisted_dict = self.get_delisted_date()
        # Generate dummy year-quarter industry classification data
        self.dummy_year_quarter_generator()
        # Set start year
        self.df_industry = self.df_industry[
            self.df_industry["year"] >= Setting.sample_start_year
        ]

    def get_delisted_date(self):
        return (
            ListedDelistedDate()
            .df_listed.set_index("stock")["delisted_date"]
            .fillna(pd.Timestamp("now").floor("D"))
            .to_dict()
        )

    def dummy_year_quarter_func(self, df: pd.DataFrame) -> pd.DataFrame:
        """`apply` function to generate dummy year-quarter data"""
        # Generate dummy date
        df_dummy = pd.DataFrame(
            pd.date_range(
                start=df["implement_date"].min(),
                end=self.delisted_dict.get(df.name, pd.Timestamp("now").floor("D")),
                freq="Q",
            ),
            columns=["date"],
        )
        # Generate `year` and `quarter` columns
        df_dummy["year"] = df_dummy["date"].dt.year
        df_dummy["quarter"] = df_dummy["date"].dt.quarter
        # Merge and return data
        return pd.merge(
            df, df_dummy.drop(columns="date"), on=["year", "quarter"], how="outer"
        )

    def dummy_year_quarter_generator(self) -> None:
        """Year and Quarter Generator"""
        # Generate `year` and `quarter` columns
        self.df_industry["year"] = self.df_industry["implement_date"].dt.year
        self.df_industry["quarter"] = self.df_industry["implement_date"].dt.quarter
        # Generate dummy year-quarter data
        self.df_industry = (
            self.df_industry.groupby("stock")
            .apply(lambda df: self.dummy_year_quarter_func(df))
            .drop(columns=["stock", "implement_date"])
            .reset_index()
            .drop(columns="level_1")
            .sort_values(by=["stock", "year", "quarter"])
        )
        # Forward fill nan `industry_code`
        self.df_industry[["industry_code"]] = self.df_industry.groupby("stock")[
            ["industry_code"]
        ].ffill()


@Cache(file_path=f"{Setting.cache_path}/industry_classification.csv", test=False)
def get_industry_classification():
    return IndustryClassification().df_industry


if __name__ == "__main__":
    # df_market = MarketType(
    #     # file_name="market_type.csv", columns=["stock", "market_type"]
    # ).df_market_type
    # ic(df_market)
    # df_listed = ListedDelistedDate().df_listed
    # ic(df_listed)
    # df_industry = IndustryClassification().df_industry
    # ic(df_industry)
    df_industry = get_industry_classification()
    ic(df_industry)
