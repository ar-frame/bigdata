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

from RSI.stg import STG


class Shipan(STG):
    RUN_TYPE_STATIC = 'REAL'

    def __init__(self, **params):
        print(params)
        super().__init__(**params)
        self.datashape = []
        self.tickcount = 0

    def __del__(self):
        print('class del...')

    def data_handler(self, data):
        super().data_handler(data)
        trade = self.trade
        try:
            intsep = int(self.config.get('trade', 'RSI_BAR_NUM'))
            row = data
            if len(self.datashape) < intsep:
                print('loading data...', len(self.datashape))
                self.datashape.append(data)
            else:
                self.tickcount = self.tickcount + 1
                self.datashape.append(data)
                self.datashape.pop(0)
                extra = self.tick_data(row, self.datashape)
                ptimef1 = func.transTimeToTimedateF1(row['time'], isUTC=False)
                tdres = trade.getTradeResult(ptime=ptimef1, price=row['close'])
                # print(extra)
                row['price'] = row['close']

                # if self.config.get('set', 'PRINT_RUNTIME_TRACE') == 'yes':
                #     # trade.dumpTrade()
                #     trade.dumpTrade(ptime=ptimef1, price=row['close'])

                stgcfg = cfg.getAccountStgInitCfg(self.account_name)
                stginfo = {"name": stgcfg.get("info", "name"), "des": stgcfg.get("info", "des"),
                           "variety": self.tradeVariety}
                recordstr = trade.getTotalProfitFromRecord(recordStr=True)

                tick_data = row
                tick_data['extra'] = extra
                if tdres is None:
                    stockdetails = ''
                    unpayfee = 0
                else:
                    stockdetails = tdres.get("result_str")
                    unpayfee = tdres.get("profit")

                pushdata = {"stginfo": stginfo, "tick_data": tick_data, "tradedetails": recordstr,
                            "stockdetails": stockdetails, "unpayfee": unpayfee}

                t = threading.Thread(target=func.setAccountTickData,
                                     args=([self.account_name, pushdata]),
                                     name='pushdataT')
                t.start()
                # res = func.setAccountTickData(self.account_name, pushdata)
                # print(res)

        except Exception as e:
            print("data handle e:", e)
            traceback.print_exc()

''
if __name__ == "__main__":

    # Shipan(account_name='dtest3').start()
    s = Shipan(account_name='trx')
    # s.start()

    # res = s.trade.addOrder('buy', currency=15, price=29222)
    # res = s.trade.get_accounts()
    # print(res)

    # accounts = s.trade.get_accounts()
    # print(accounts)

    # res = s.trade.addOrder('buy', currency=10, price=25000)
    # print(res)

    # while True:
    #     tickdata = s.trade.getKline()
    #     print(tickdata)
    #     time.sleep(1)
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
