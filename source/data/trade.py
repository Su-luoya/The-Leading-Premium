# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-07 15:43:01
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-07 16:27:56
"""
df_ret = get_stock_return() \n
traded_value, total_value \n
return_with_dividend, return_without_dividend
"""

import sys
from pathlib import Path

import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.data.macro import RFR
from source.modules.cache import Cache
from source.modules.setting import Setting
from source.modules.tools import singleton


@singleton
class ST(object):
    def __init__(
        self, file_name="st.csv", columns: list[str] = ["stock", "date", "trade_state"]
    ) -> None:
        self.df_st: pd.DataFrame = pd.read_csv(f"{Setting.trade_path}/{file_name}")
        self.df_st.columns = columns
        self.df_st["date"] = pd.to_datetime(self.df_st["date"])
        self.df_st["year"] = self.df_st["date"].dt.year
        self.df_st["quarter"] = self.df_st["date"].dt.quarter
        # `trade_state` determination
        self.df_st["is_st"] = self.df_st["trade_state"] != 1
        self.df_st = self.df_st.drop(columns="trade_state")
        # Generate is_quarter_st data
        self.df_st = (
            self.df_st.astype({"stock": int})
            .groupby(["stock", "year", "quarter"])[["is_st"]]
            .sum()
            .astype({"is_st": bool})
            .astype({"is_st": int})
            .reset_index(drop=False)
        )


class Ret(object):
    def __init__(
        self,
        file_name: str = "return.csv",
        columns: list[str] = [
            "stock",
            "date",
            "market_type",
            "traded_value",
            "total_value",
            "return_with_dividend",
            "return_without_dividend",
        ],
    ) -> None:
        self.df_ret = pd.read_csv(f"{Setting.trade_path}/{file_name}")
        self.df_ret.columns = columns
        self.delete_market()
        self.type_convert()
        # Set sample start year
        self.df_ret = self.df_ret[
            self.df_ret["year"]
            >= Setting.sample_start_year
            + Setting.sample_periods // Setting.shift_period
        ].drop(columns="date")
        self.delete_st()
        self.rfr_adjust()

    def delete_market(self) -> None:
        """'Delete market_type not in [1, 4]"""
        self.df_ret = self.df_ret[
            self.df_ret["market_type"].isin(Setting.market_list)
        ].drop(columns="market_type")

    def type_convert(self) -> None:
        """Generate year and quarter"""
        self.df_ret["date"] = pd.to_datetime(self.df_ret["date"])
        self.df_ret["year"] = self.df_ret["date"].dt.year
        self.df_ret["quarter"] = self.df_ret["date"].dt.quarter
        self.df_ret["month"] = self.df_ret["date"].dt.month

    def delete_st(self) -> None:
        """Delete ST data"""
        # Merge ST data
        self.df_ret = pd.merge(
            self.df_ret, ST().df_st, on=["stock", "year", "quarter"], how="inner"
        )
        # Delete ST Data
        self.df_ret = self.df_ret[~self.df_ret["is_st"].astype(bool)].drop(
            columns="is_st"
        )

    def rfr_adjust(self) -> None:
        """Calculate excess return of rate"""
        # Merge risk-free rate data
        self.df_ret = pd.merge(
            self.df_ret, RFR().df_rfr, on=["year", "month"], how="left"
        )
        # Minus the risk-free rate
        self.df_ret["return_with_dividend"] = (
            self.df_ret["return_with_dividend"] - self.df_ret["rfr"]
        )
        self.df_ret["return_without_dividend"] = (
            self.df_ret["return_without_dividend"] - self.df_ret["rfr"]
        )
        # Drop rfr column
        self.df_ret = self.df_ret.drop(columns="rfr").sort_values(
            by=["stock", "year", "quarter", "month"]
        )


@Cache(file_path=f"{Setting.cache_path}/stock_return.csv", test=False)
def get_stock_return():
    return (
        Ret()
        .df_ret[
            [
                "stock",
                "year",
                "quarter",
                "month",
                "traded_value",
                "total_value",
                "return_with_dividend",
                "return_without_dividend",
            ]
        ]
        .dropna()
    )


if __name__ == "__main__":
    # df_st = ST().df_st
    # ic(df_st)

    # df_ret = Ret().df_ret

    # ic(df_ret)
    df_ret = get_stock_return()
    ic(df_ret)
