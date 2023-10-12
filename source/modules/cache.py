# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 09:12:49
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-12 17:53:36
"""
cp() \n
@Cache(file_path="test.csv", test=False)
"""

import sys
from pathlib import Path
from typing import Callable

import pandas as pd
from icecream import ic


ic.configureOutput(prefix="")

sys.path.append(str(Path.cwd()))
from source.modules.setting import Setting
from source.modules.tools import cp


class Cache(object):
    """
    Data Cache Wrapper.
    --------

    Args:
    --------
        file_path (str): The relative path of the csv/excel file.
        test (bool, optional): If True, do not read or cache data. Defaults to True.
        func (Callable[..., pd.DataFrame]): The function/method to be executed.

    Usages:
    -------
        >>> from pandas import DataFrame
        >>> @Cache(file_path="test/test.csv", test=False)
        >>> def func(*args, **kwargs) -> DataFrame:
        >>>     ...
        >>>     return df
        >>> df: DataFrame = func(*args, **kwargs)
    """

    # Prevent repeat cache reads.
    path_dict: dict[Path, pd.DataFrame] = {}

    def __init__(self, file_path: str, test: bool = True) -> None:
        self.file_path: str = file_path  # User's path
        self.cache_path: Path = Path(
            f"{Setting.data_path}/{file_path}"
        ).resolve()  # Absolute path
        self.test: bool = test
        self.file_type: str | None = None

    def __call__(
        self, func: Callable[..., pd.DataFrame]
    ) -> Callable[..., pd.DataFrame | None]:
        def wrapper(*args, **kwargs) -> pd.DataFrame | None:
            # If argument "test" is True,
            # execute the given function/method without reading or saving data.
            if self.test:
                cp(
                    f'Testing "{func.__name__}"...',
                    color="yellow",
                )
                self.path_dict[self.cache_path] = func(*args, **kwargs)
                return self.path_dict[self.cache_path]
            # Prevent duplicate cache reads.
            if self.cache_path in self.path_dict:
                return self.path_dict[self.cache_path]
            # Determine the file type.
            self.file_type = self.cache_path.suffix[1:]
            # Check file existence.
            if self.cache_path.exists():
                # The cache exists, load data from the file.
                cp(f"{self.file_path} found!", color="yellow")
                cp(f"Read data from {self.file_path}...", color="blue")
                df: pd.DataFrame = self.read_file()
            else:
                # The cache does not exist,
                # call the function/method and save return data to the file.
                cp(f"{self.file_path} not found!", color="red")
                cp(f"Save to {self.file_path}...", color="blue")
                df: pd.DataFrame = self.save_file(func(*args, **kwargs))
            # Record data that has been read.
            self.path_dict[self.cache_path] = df
            return df

        return wrapper

    def read_file(self) -> pd.DataFrame:
        """Read data from a csv or excel file."""
        if self.file_type == "csv":
            return pd.read_csv(self.cache_path)
        elif self.file_type == "xlsx":
            return pd.read_excel(self.cache_path)
        else:
            raise ValueError("File type not supported!")

    def save_file(self, df: pd.DataFrame) -> pd.DataFrame:
        """Save data into a csv or excel file."""
        # Directory generator.
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        # Read cache file.
        if self.file_type == "csv":
            df.to_csv(self.cache_path, index=False)
        elif self.file_type == "xlsx":
            df.to_excel(self.cache_path, index=False)
        else:
            raise ValueError("File type not supported!")
        return df


class TestCacheData:
    """Test DataFrame"""

    @Cache(file_path="cache/test1.csv", test=False)
    def test_df1(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9],
            ],
            columns=["A", "B", "C"],
        )

    @Cache(file_path="test/test1.csv", test=False)
    def test_df2(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 10],
            ],
            columns=["D", "E", "F"],
        )


if __name__ == "__main__":
    test = TestCacheData()
    ic(test.test_df1())
    ic(test.test_df2())
