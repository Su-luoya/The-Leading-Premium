# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-03-17 20:35:37
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-03-17 21:46:26


from typing import List

import numpy as np
import pandas as pd
from icecream import ic

from cache import Cache, try_read_cached_data

ic.configureOutput(prefix="")


class Settings(object):
    """Settings class."""

    # datetime that needs to be disposed after delisted
    delete_date_range_after_delisted: dict[str, int] = {
        "year": 1,
        "month": 0,
        "week": 0,
        "day": 0,
    }


class STData(object):
    """
    ST Data Preprocessing.
    --------

    Args:
    --------
        df_st (DataFrame): ST DataFrame.
        st_columns (List[str]): Columns in order. Defaults to ["stock", "date", "trade_state"].

    ValueError: Make sure your data meets the requirements!
    --------
        1. Check whether the columns are in the correct order. ⭐️
        2. Check for missing values in the data. ⭐️
        3. Check for duplicates.
        4. ...

    Usages:
    --------
        >>> import pandas as pd  ⬇ Your ST Data File (No Missing Values)
        >>> df_st = pd.read_csv("./data/st.csv")
                 ⬇ Make sure your columns are in order!
               stock        date  trade_state
            0      1  2013/10/18            1
            1      1  2013/10/19            1
            2      2  2013/10/18            0
            3      2  2013/10/19            0
        >>> df_st: pd.DataFrame = STData(
        ... df_st=df_st,
        ... st_columns=["stock", "date", "trade_state"]
        ... ).df_st
        >>> print(df_st)
    """

    def __init__(
        self,
        df_st: pd.DataFrame,
        st_columns: List[str] = ["stock", "date", "trade_state"],
    ) -> None:
        # Check for columns number and missing value
        if len(df_st.columns) != 3 or df_st.isnull().values.any():
            raise ValueError("Make sure that your st data meets the requirements!")
        # Reset columns
        df_st.columns = st_columns
        # Initialize self.df_st
        self.df_st: pd.DataFrame = df_st
        # Convert data type
        self.__type_convert()

    def __type_convert(self) -> None:
        """
        Data Type Conversation
        --------
            stock (int)

            date (datetime64)

            is_st (bool)
        """
        # stock
        self.df_st["stock"] = self.df_st["stock"].astype(int)
        # date
        self.df_st["date"] = pd.to_datetime(self.df_st["date"])
        # trade_state
        self.df_st["is_st"] = self.df_st["trade_state"] != 1
        self.df_st.drop(columns="trade_state", inplace=True)
        # sort values
        self.df_st: pd.DataFrame = self.df_st.sort_values(by=["stock", "date"])


class ListedData(object):
    """
    Listed and Delisted Data Preprocessing.
    --------
    Args:
    --------
        df_listed (DataFrame): Listed and Delisted DataFrame.
        listed_columns (List[str]): Columns in order. Defaults to ["stock", "listed_date", "delisted_date"].

    ValueError: Make sure your data meets the requirements!
    --------
        1. Check whether the columns are in the correct order. ⭐️
        2. Check for duplicates.
        3. ...

    Usages:
    --------
        >>> import pandas as pd  ⬇ Your Listed and Delisted Data File
        >>> df_listed = pd.read_csv("./data/listed_delisted_date.csv")
                 ⬇ Make sure your columns are in order!
               stock  listed_date  delisted_date
            0      1   2013/10/18     2019/11/11
            1      2   2009/12/13            NaN
        >>> df_listed: pd.DataFrame = ListedData(
        ... df_listed=df_listed, ⬇ Make sure your columns are in order!
        ... listed_columns=["stock", "listed_date", "delisted_date"]
        ... ).df_listed
        >>> print(df_listed)
    """

    def __init__(
        self,
        df_listed: pd.DataFrame,
        listed_columns: List[str] = ["stock", "listed_date", "delisted_date"],
    ) -> None:
        # Check for columns number
        if len(df_listed.columns) != 3:
            raise ValueError("Make sure that your listed data meets the requirements!")
        # Reset columns
        df_listed.columns = listed_columns
        # Initialize self.df_listed
        self.df_listed: pd.DataFrame = df_listed
        # Convert data type
        self.__type_convert()

    def __type_convert(self) -> None:
        """
        Data Type Conversation
        --------
            stock (int)

            listed_date (datetime64)

            delisted_date (datetime64)
        """
        # fill np.nan
        self.df_listed.fillna(np.nan, inplace=True)
        # stock
        self.df_listed["stock"] = self.df_listed["stock"].astype(int)
        # listed_date
        self.df_listed["listed_date"] = pd.to_datetime(self.df_listed["listed_date"])
        # delisted
        self.df_listed["delisted_date"] = pd.to_datetime(
            self.df_listed["delisted_date"]
        )
        # sort values
        self.df_listed: pd.DataFrame = self.df_listed.sort_values(by=["stock"])


class Preprocess(object):
    """
    Delete quarters containing st data and delete data from the first year after listed.

    Args:
    --------
        df_st (DataFrame): ST DataFrame.
        df_listed (DataFrame): Listed and Delisted DataFrame.
        st_columns (List[str]): Columns in order. Defaults to ["stock", "date", "trade_state"].
        listed_columns (List[str]): Columns in order. Defaults to ["stock", "listed_date", "delisted_date"].

    File Examples:
    --------
        🌟 Make sure your columns are in order!
        >>> ST File (NO NaN!)
               stock        date  trade_state
            0      1  2013/10/18            1
            1      1  2013/10/19            1
            2      2  2013/10/18            0
            3      2  2013/10/19            0
        >>> Listed and Delisted File (NO NaN in "stock" & "listed_date")
               stock  listed_date  delisted_date
            0      1   2013/10/18     2019/11/11
            1      2   2009/12/13            NaN

    Usages:
    --------
        >>> df_result: pd.DataFrame = Preprocess(
        ...     st_file_name="st.csv", ⬅ Your File Name
        ...     listed_file_name="listed and delisted.csv",
        ...     st_columns=["stock", "date", "trade_state"], ⬅ Columns in Order
        ...     listed_columns=["stock", "listed_date", "delisted_date"],
        ... ).result
        >>> print(df_result)

    """

    def __init__(
        self,
        st_file_name: str,
        listed_file_name: str,
        st_columns: List[str] = ["stock", "date", "trade_state"],
        listed_columns: List[str] = ["stock", "listed_date", "delisted_date"],
    ) -> None:
        # Initialize
        self.st_file_name: str = st_file_name
        self.listed_file_name: str = listed_file_name
        self.st_columns: List[str] = st_columns
        self.listed_columns: List[str] = listed_columns
        # Start to work!
        self.cache: Cache = Cache()

    @property
    def result(self) -> pd.DataFrame:
        """Data preprocessed."""
        return try_read_cached_data(
            cache_instance=self.cache,
            func=self.__work,
            file_name="preprocessed_data.csv",
        )

    def merge_data(self) -> None:
        """Merge df_st and df_listed."""
        self.df_pre: pd.DataFrame = pd.merge(
            STData(self.cache.data(file_name=self.st_file_name), self.st_columns).df_st,
            ListedData(
                self.cache.data(file_name=self.listed_file_name), self.listed_columns
            ).df_listed,
            how="left",
            on="stock",
        )

    def delete_st_quarter(self) -> None:
        """Delete quarters containing st data."""
        # Construct year and quarter from date
        self.df_pre["year"] = self.df_pre["date"].dt.year
        self.df_pre["quarter"] = self.df_pre["date"].dt.quarter
        # Get all the quarters containing st data
        self.df_pre = pd.merge(
            self.df_pre,
            (self.df_pre.groupby(["stock", "year", "quarter"])["is_st"].sum())
            .astype(bool)
            .rename("is_quarter_st"),
            how="left",
            on=["stock", "year", "quarter"],
        )
        # Delete quarters containing st data
        self.df_pre = self.df_pre[~self.df_pre["is_quarter_st"]].drop(
            columns="is_quarter_st"
        )

    def delete_first_year(self) -> None:
        """Delete data from the first year after listed."""
        # Set delete date range after delisted
        delete_date_range_after_delisted: dict[
            str, int
        ] = Settings.delete_date_range_after_delisted
        # Delete 1-year-data after delisted
        self.df_pre = self.df_pre[
            self.df_pre["date"]
            >= (
                self.df_pre["listed_date"]
                # Set date offset
                + pd.tseries.offsets.DateOffset(
                    years=delete_date_range_after_delisted["year"],
                    months=delete_date_range_after_delisted["month"],
                    weeks=delete_date_range_after_delisted["week"],
                    days=delete_date_range_after_delisted["day"],
                )
            )  # type: ignore
        ]

    def __work(self) -> pd.DataFrame:
        """Work Function."""
        self.merge_data()
        self.delete_st_quarter()
        self.delete_first_year()
        return self.df_pre[["stock", "date"]]


if __name__ == "__main__":
    # cache = Cache()
    # df_st: pd.DataFrame = cache.data(file_name="st.csv").sort_values(["stock", "date"])
    # df_st = df_st[pd.to_datetime(df_st["date"]) >= pd.to_datetime("2015-01-01")]
    # df_st.to_csv("cache/st.csv", index=False)
    # df_listed = cache.data(file_name="ipo.csv")
    df_result: pd.DataFrame = Preprocess(
        st_file_name="st.csv",
        listed_file_name="ipo.csv",
        st_columns=["stock", "date", "trade_state"],
        listed_columns=["stock", "listed_date", "delisted_date"],
    ).result
    ic(df_result)
    ...
