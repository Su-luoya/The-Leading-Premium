# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 09:12:59
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-14 15:25:31


import os


class Setting(object):
    # Directory to store data files
    data_dir = '/Users/suluoya/Desktop/LLData'
    
    # & src/modules/cache.py
    # The name of directory where the cached data is located
    cache_dir: str = f"{data_dir}/cache"

    # & cache directory
    # The name of directory where stock basic information data is located
    basic_info_dir: str = "origin/basic_info"


if __name__ == "__main__":
    print(Setting.cache_dir)
