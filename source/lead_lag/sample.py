# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-04 21:21:31
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-05 14:24:18


import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.data.basic import get_industry_classification
from source.data.cashflow import get_cashflow
from source.modules.setting import Setting
from source.modules.tools import singleton


@singleton
class Sample(object):
    """
    (20+4*2+1)-quarters-window for a sample period
    """

    def __init__(self) -> None:
        # Merge cashflow data and industry classification data
        self.df_cash = pd.merge(
            get_cashflow(),  # type: ignore
            get_industry_classification(),  # type: ignore
            on=["stock", "year", "quarter"],
            how="inner",
        )
        # Generate year_quarter column
        self.df_cash["year_quarter"] = self.df_cash[["year", "quarter"]].apply(
            lambda row: pd.Period(year=row["year"], quarter=row["quarter"], freq="Q"),
            axis=1,
        )
        # Generate period range
        self.period_range: np.ndarray[pd.Period, Any] = self.df_cash[
            "year_quarter"
        ].unique()

    def get_samples(self):
        """
        Sample Generator
        ------

        Returns:
        ------
            >>> {"quarter" : Period('2010Q1', 'Q-DEC'), "df_cash" : pd.DataFrame}, ...
        """
        for period_index in filter(
            lambda x: len(x) >= Setting.sample_periods,
            [
                self.period_range[i : i + Setting.sample_periods]
                for i in range(len(self.period_range))
            ],
        ):
            yield {
                "quarter": period_index[-1],
                "df_cash": self.df_cash[
                    self.df_cash["year_quarter"].isin(period_index)
                ].drop(columns="year_quarter"),
            }


if __name__ == "__main__":
    samples = Sample().get_samples()
    ic(next(samples))
    ic(next(samples))
