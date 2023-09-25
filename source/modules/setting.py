# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 09:12:59
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-25 21:39:53


from icecream import ic


class Setting(object):
    """Settings"""

    # & Data Structure
    # Data path
    data_path: str = "data"

    # 1. The name of directory where the cached data is located
    cache_path: str = f"{data_path}/cache"

    # 2. The name of directory where original data is located
    origin_path: str = f"{data_path}/origin"

    # 2.1 Basic information of stocks
    basic_path: str = f"{origin_path}/basic"

    # 2.2 Macro-indicators
    macro_path: str = f"{origin_path}/macro"
    
    # & Sample
    # Sample start year
    sample_start_year = 2003


if __name__ == "__main__":
    ic(Setting.basic_path)
