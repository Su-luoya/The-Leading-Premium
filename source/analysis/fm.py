# -*- coding: utf-8 -*-
# @Author: 昵称有六个字
# @Date:   2023-10-18 17:41:15
# @Last Modified by:   昵称有六个字
# @Last Modified time: 2023-10-18 17:41:44


import sys
from pathlib import Path
from time import time

import numpy as np
import pandas as pd
from icecream import ic

ic.configureOutput(prefix="")
sys.path.append(str(Path.cwd()))
from source.analysis.sample import TestSample
from source.data.basic import get_industry_classification
from source.data.trade import StockReturn
from source.modules.cache import Cache, cp
from source.modules.setting import Setting
from source.modules.tools import TTest, singleton


class FMRegression(object):
    ...
