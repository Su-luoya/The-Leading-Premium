# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-18 20:33:49
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-18 21:11:34


import sys
from pathlib import Path

import numpy as np
import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.modules.cache import Cache
from source.modules.setting import Setting
from source.modules.tools import singleton


class BM(object):
    def __init__(
        self,
        file_name: str = "BM.csv",
        columns: list[str] = ["stock", "year", "quarter", "BM"],
    ) -> None:
        self.df_bm = pd.read_csv(f"{Setting.finance_path}/{file_name}")
        self.df_bm.columns = columns
        self.df_bm = self.df_bm.astype(
            {"stock": int, "year": int, "quarter": int, "BM": float}
        ).dropna()


class Size(object):
    def __init__(
        self,
        file_name: str = "size.csv",
        columns: list[str] = ["stock", "year", "quarter", "month", "size"],
    ) -> None:
        self.df_size = pd.read_csv(f"{Setting.finance_path}/{file_name}")
        self.df_size.columns = columns
        self.df_size = self.df_size.astype(
            {"stock": int, "year": int, "quarter": int, "month": int, "size": float}
        ).dropna()
        self.df_size["size"] = np.log(self.df_size["size"])


if __name__ == "__main__":
    # df_bm = BM().df_bm
    # ic(df_bm)
    df_size = Size().df_size
    ic(df_size)
