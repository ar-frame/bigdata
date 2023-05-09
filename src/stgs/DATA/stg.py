#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

'test for dev stg moudule'
__author__ = 'dpbtrader'
import sys
sys.path.append('../../')
from DataStream import DataStream

import traceback
import tools

from alive_progress import alive_bar

try:
    import thread
except ImportError:
    import _thread as thread
import os
import func
import cfg
from Trade import Trade

class STG(DataStream):
    RUN_TYPE_STATIC = 'VIRTUAL'
    def __init__(self, account_name):
        self.account_name = account_name
        self.trade = Trade(account_name)
        print(self.RUN_TYPE_STATIC)
        self.RUN_TYPE = self.RUN_TYPE_STATIC
        self.trade.RUN_TYPE = self.RUN_TYPE_STATIC
        stg_cfg = cfg.getAccountCfg(account_name, stg=True)
        self.config = stg_cfg
        key_cfg = cfg.getAccountCfg(account_name, stg=False)
        self.key_config = key_cfg
        self.tradeVariety = self.config.get('set', 'TRADE_VARIETY')
        super().__init__(account_name)





if __name__ == "__main__":
    Paint('dtest2').start()

    # print(Paint.RUN_TYPE_STATIC)
    # func.setAccountProfit('dtest', 'virtual', 123, 22)
    # res = func.getAccountProfit('dtest', 'virtual')
    # print(res)
    # setprofit = cfg.getFetch().getObject('server.Data', 'setDatakey', ['profit', 12.0])
    # getprofit = cfg.getFetch().getFloat('server.Data', 'getDataByKey', ['profit'])
    # print(setprofit, getprofit)
