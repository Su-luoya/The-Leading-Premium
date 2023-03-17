# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-03-17 21:01:59
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-03-17 22:00:40


from typing import List

import pandas as pd
from icecream import ic

from cache import Cache, try_read_cached_data

ic.configureOutput(prefix="")


class IndustryData(object):
    """
    Industry Data Preprocessing.
    --------

    Args:
    --------
        df_industry (DataFrame): Industry DataFrame.
        industry_columns (List[str]): Columns in order. Defaults to ["stock", "industry_code", "industry_name", "implement_date"].

    ValueError: Make sure your data meets the requirements!
    --------
        1. Check whether the columns are in the correct order. ⭐️
        2. Check for duplicates.
        3. ...

    Usages:
    --------
        >>> import pandas as pd
        >>> df_st: pd.DataFrame = pd.read_csv("./data/industry.csv")
                  ⬇ Make sure your columns are in order!
                stock  industry_code  industry_name	 implement_date
            0       1            J66	 货币金融服务	   1991/04/03
            1       2            K70	    房地产业	  1991/01/29
        >>> df_industry: pd.DataFrame(
        ...     df_industry=df_industry,
        ...     industry_columns=[
        ...         "stock",
        ...         "industry_code",
        ...         "industry_name",
        ...         "implement_date",
        ...     ]
        ... ).df_industry
        >>> print(df_industry)
    """

    def __init__(
        self,
        df_industry: pd.DataFrame,
        industry_columns: List[str] = [
            "stock",
            "industry_code",
            "industry_name",
            "implement_date",
        ],
    ) -> None:
        # Check for columns number
        if len(df_industry.columns) != 4:
            raise ValueError("Make sure that your listed data meets the requirements!")
        # Reset columns
        df_industry.columns = industry_columns
        # Initialize self.df_industry
        self.df_industry = df_industry
        # Convert data type
        self.__type_convert()

    def __type_convert(self) -> None:
        """
        Data Type Conversation
        --------
            stock (int)

            industry_code (str)

            industry_name (str)

            implement_date (datetime64)
        """
        # stock
        self.df_industry["stock"] = self.df_industry["stock"].astype(int)
        # implement_date
        self.df_industry["implement_date"] = pd.to_datetime(
            self.df_industry["implement_date"]
        )
        # sort values
        self.df_industry: pd.DataFrame = self.df_industry.sort_values(
            by=["stock", "implement_date"]
        )


if __name__ == "__main__":
    df_industry = pd.read_csv("data/industry.csv")
    df_industry = IndustryData(
        df_industry=df_industry,
        industry_columns=[
            "stock",
            "industry_code",
            "industry_name",
            "implement_date",
        ],
    ).df_industry
    ic(df_industry)
    ...
