# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 09:12:59
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-18 20:54:53


from icecream import ic


class Setting(object):
    """Settings"""

    # & Data Structure
    # Data path
    data_path: str = "data"

    # 1. The name of directory where the cached data is located
    cache_path: str = "cache"

    # 2. The name of directory where original data is located
    origin_path: str = f"{data_path}/origin"

    # 2.1 Basic information of stocks
    basic_path: str = f"{origin_path}/basic"

    # 2.2 Macro-indicators
    macro_path: str = f"{origin_path}/macro"

    # 2.3 Cash flow
    cashflow_path: str = f"{origin_path}/cashflow"

    # 2.4 Trade
    trade_path: str = f"{origin_path}/trade"
    
    # 2.5 Finance
    finance_path: str = f"{origin_path}/finance"
    

    # & Sample
    # Sample start year
    sample_start_year = 2003
    # Window period and shift period
    window_period: int = 20
    shift_period: int = 2
    sample_periods: int = shift_period * 2 + window_period + 1
    # Market type: 1=上证A股市场 (不包含科创板），2=上证B股市场，4=深证A股市场（不包含创业板），8=深证B股市场，16=创业板， 32=科创板，64=北证A股市场
    market_list: list[int] = [1, 4]
    # Annotation delay max periods
    delay_max_period = 2
    # Balance panel or not
    is_balance_panel = False
    # Inflation Adjust: CPI or PPI
    price_index: str = "PPI"
    # GDP column: "GDP", "GDP_1", "GDP_2", "GDP_3"
    gdp_column: str = "GDP"

    # & Cashflow Measures
    # EBIT, EBITDA, EBIT(TTM) or EBITDA(TTM)?
    ebitda_columns = ["EBIT", "EBIT_TTM", "EBITDA", "EBITDA_TTM"]
    # Income statement
    income_columns: list[str] = [
        "total_operating_income",
        "operating_income",
        "operating_profit",
        "total_profit",
        "net_profit",
    ]
    # Cashflow statement
    cashflow_columns: list[str] = [
        "operating_cashflow",
        "investing_cashflow",
        "financing_cashflow",
        "cash_increase",
    ]
    # Conclude
    cashflow_measures = ebitda_columns + income_columns + cashflow_columns

    # & Empirical Analysis
    # Shift LL rank to pair return data
    shift_rank_period: int = delay_max_period
    # Industry number that lead (lag) portfolio contains
    lead_group_industry_number: int = 9
    lag_group_industry_number: int = 10


if __name__ == "__main__":
    ic(Setting.basic_path)
