# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-03-17 20:22:39
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-03-17 20:44:05


import contextlib
import os
from pprint import pprint
from typing import Callable

import pandas as pd
import pretty_errors
from icecream import ic

ic.configureOutput(prefix="")


class Cache(object):
    """
    Data Cache.
    --------

    Args:
    --------
        path (str, optional): Cache Data Directory Path. Defaults to '.'.
        name (str, optional): Cache Data Directory Name. Defaults to "cache".

    Usages:
    --------
            Initialization
            >>> import pandas as pd
            >>> cache: Cache = Cache(path='.', name='temp')

            Check file existence
            >>> cache.check_file(file_path='./cache/test.csv')

            Cache data
            >>> df: pd.DataFrame = cache.data(
            ...     df=pd.DataFrame([1, 2, 3]),
            ...     file_name="test.csv"
            ... )
            >>> print(df)

            Read cached data
            >>> df: pd.DataFrame = cache.data(file_name="test.csv")
            >>> print(df)
    """

    def __init__(self, path: str = ".", name: str = "temp") -> None:
        # Construct cache path
        self.cache_path: str = f"{path}//{name}"

    def make_dir(self) -> None:
        """Make an empty directory"""
        with contextlib.suppress(Exception):
            os.mkdir(self.cache_path)

    def check_file(self, file_path: str) -> bool:
        """
        Check File Existence.
        --------

        Args:
        --------
            file_path (str): File Path.

        Returns:
        --------
            bool: If file exists → True.
        """
        return os.path.isfile(file_path)

    def data(self, file_name: str, df: pd.DataFrame = pd.DataFrame()) -> pd.DataFrame:
        """
        Data Cache Function.
        --------

        Args:
        --------
            file_name (str): File Name.
            df (pd.DataFrame, optional): Data needs to be cached. Defaults to an empty Dataframe.

        Raises:
        --------
            ValueError: File doesn't exist, and df is empty.

        Returns:
        --------
            pd.DataFrame: Cached Data.
        """
        # Construct file path
        file_path: str = f"{self.cache_path}//{file_name}"
        # Check weather df is empty, and file hasn't been cached
        if df.empty and not self.check_file(file_path=file_path):
            raise ValueError(f"{file_path} doesn't exist, and df is empty")
        # Determine file type
        file_type: str = file_name.split(".")[-1]
        # If df is empty, or the file already exists, read the cached data directly
        if df.empty or self.check_file(file_path=file_path):
            ic(f"Imported {file_name} from {self.cache_path}")
            return (
                pd.read_csv(file_path)
                if file_type == "csv"
                else pd.read_excel(file_path)
            )
        # If df is not empty, and the file has not been cached, cache the data
        if file_type == "csv":
            df.to_csv(file_path, index=False)
        elif file_type == "xlsx":
            df.to_excel(file_path, index=False)
        # Log
        ic(f"Exported {file_name} to {self.cache_path}")
        # Return data
        return df


def try_read_cached_data(
    cache_instance: Cache, func: Callable[..., pd.DataFrame], file_name: str
) -> pd.DataFrame:
    """Try to read cached data
    --------

    Args:
    --------
        cache_instance (Cache): Instance initialized by class Cache.
        func (Callable): Work Function without arguments.
        file_name (str): File Name.

    Returns:
    --------
        pd.DataFrame: Cached Data

    Usages:
    --------
        >>> import pandas as pd
        >>> cache: Cache = Cache() ⬅ Initialize an instance for class Cache
        >>> df = try_read_cached_data(cache_instance=cache, func=func, file_name='test.csv')
    """
    try:
        return cache_instance.data(file_name=file_name)
    except Exception:
        return cache_instance.data(df=func(), file_name=file_name)


def __test():
    return pd.DataFrame([1, 2])


if __name__ == "__main__":
    cache: Cache = Cache()
    # df: pd.DataFrame = cache.data(file_name="test.csv")
    # ic(df)
    df = try_read_cached_data(cache_instance=cache, func=__test, file_name="test.csv")
    ic(df)
    ...
