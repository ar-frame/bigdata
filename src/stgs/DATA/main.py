#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
'test for dev stg moudule'
__author__ = 'dpbtrader'

import json
import sys
import threading
import time

sys.path.append('../../')
import traceback
from dbconn import MongoDB

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import func
import cfg
from DATA.stg import STG
class Shipan(STG):
    RUN_TYPE_STATIC = 'REAL'
    def __init__(self, **params):
        super().__init__(**params)
        mark = func.formatStoreName(self.tradeVariety)
        self.symbolmark = 'kline_' + mark

        # self.check_data_lock = func.getAccountKlineLock(self.symbolmark)
        # if self.check_data_lock:
        self.db_mongo_storekline = func.getMongoStoreObject(self.symbolmark)

    def __del__(self):
        print('class del...')
        if self.check_data_lock:
            print('release lock')
            func.releaseAccountKlineLock(self.symbolmark)

    def data_handler(self, data):
        # print('main data', data)
        t = threading.Thread(target=self.pushdbdata,
                             args=([data]),
                             name='pushdbdataT')
        t.start()

        stgcfg = cfg.getAccountStgInitCfg(self.account_name)
        stginfo = {"name": stgcfg.get("info", "name"), "des": stgcfg.get("info", "des"),
                   "variety": self.tradeVariety}
        tick_data = data
        pushdata = {"stginfo": stginfo, "tick_data": tick_data, "tradedetails": '',
                    "stockdetails": '', "unpayfee": 0}

        t = threading.Thread(target=func.setAccountTickData,
                             args=([self.account_name, pushdata]),
                             name='pushdataT')
        t.start()

    def start(self):
        print('data start.............')
        try:
            super().start()
            print('start end....')
        except Exception as e:
            print('main start exception ', e)
            cfg.write_log('stg_data_error_main_log', e)
            cfg.write_log('stg_data_error_main_log', traceback.print_exc())
            cfg.write_log('stg_data_error_main_log', 'traceback.format_exc():\n%s' % traceback.format_exc())
            time.sleep(5)
            print('main sleep restart ...')
            self.start()

    def on_error(self):
        print('main thread on error, restart...')
        self.start()

    def pushdbdata(self, data):
        self.db_mongo_storekline.insert(data)
''
if __name__ == "__main__":
    # Shipan(account_name='dtest3').start()
    s = Shipan(account_name='trx')
        # .start()
    res = s.trade.addOrder('sell', currency=25, price=0.069123)
    print(res)
    # data handler
    # ptime = func.transTimeToTimedate(row['time'], isUTC=False)
    # if self.tickcount < 2:
    #     self.trade.addOrder('buy', 25, row['price'], ptime)
    # elif self.tickcount < 5:
    #     self.trade.addOrder('sell', 25, row['price'], ptime)
    # elif self.tickcount == 5:
    #     res = self.trade.cover(price=row['price'], timedate=ptime,msg="pc1")
    #     print('pc res', res)
    #     # exit()
    # elif self.tickcount < 8:
    #     self.trade.addOrder('buy', 25, row['price'], ptime)
    # elif self.tickcount < 12:
    #     self.trade.addOrder('sell', 25, row['price'], ptime)
    # elif self.tickcount == 12:
    #     res = self.trade.cover(price=row['price'], timedate=ptime, msg="pc2")
    #     print('cover res 2', res)
    # else:
    #     # self.trade.cover()
    #     self.trade.addOrder('sell', 25, row['price'], ptime)
    #     trade.dumpTrade(ptime=ptime, price=row['close'])
    #     exit()
