# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-08-17 09:12:59
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-09-14 16:46:28


from pathlib import Path

from icecream import ic


class Setting(object):
    """Settings"""
    # & Project Structure
    # Project path
    project_path: Path = Path.cwd()

    # Data path
    data_path: str = f"{project_path.parent}/LLData"

    # The name of directory where the cached data is located
    cache_path: str = f"{data_path}/cache"

    # The name of directory where original data is located
    origin_path: str = f"{data_path}/origin"


if __name__ == "__main__":
    print(Setting.data_path)
