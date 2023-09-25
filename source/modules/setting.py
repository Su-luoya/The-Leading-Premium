# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 09:12:59
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-25 20:05:42


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
    basic_path = f"{origin_path}/basic"
    
    # 2.2 Macro-indicators
    macro_path = f"{origin_path}/macro"


if __name__ == "__main__":
    ic(Setting.basic_path)
