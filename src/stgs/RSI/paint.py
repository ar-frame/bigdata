#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

'test for dev stg moudule'
__author__ = 'dpbtrader'
import sys
sys.path.append('../../')
import traceback
from alive_progress import alive_bar

import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import func
import cfg

from RSI.stg import STG

class Paint(STG):
    RUN_TYPE_STATIC = 'VIRTUAL'
    def __init__(self, **params):
        print(params)
        super().__init__(**params)

    def start(self):
        aname = self.account_name
        print("start loop check name..." + aname)
        trade = self.trade
        starttime = self.config.get('test', 'STARTTIME')
        endtime = self.config.get('test', 'ENDTIME')
        try:
            logtimemsg = '回测:' + starttime + '-' + endtime
            trade.logOrders(msg=logtimemsg, isclear=True)
            datas = cfg.getFetch().getArray('server.Data', 'getKlineHisData', [self.tradeVariety, starttime, endtime])
            intsep = int(self.config.get('trade', 'RSI_BAR_NUM'))
            with alive_bar(len(datas) - intsep) as bar:
                for i in range(len(datas)):
                    moveindex = i + intsep
                    if moveindex > len(datas) - 1:
                        break
                    row = datas[moveindex]
                    datashape = datas[i: moveindex]
                    extra = self.tick_data(row, datashape)
                    datas[moveindex]['extra'] = extra
                    bar()
            stgstr = "\n" + cfg.getAccountCfg(self.account_name, stg=True, raw=True)
            cfg.write_log(self.trade.getLogMark(), stgstr)
            stgcfg = cfg.getAccountStgInitCfg(self.account_name)
            stginfo = {"name": stgcfg.get("info", "name"), "des": stgcfg.get("info", "des"),
                       "variety": self.tradeVariety, "ptime": logtimemsg}
            recordstr = trade.getTotalProfitFromRecord(recordStr=True)
            tdres = trade.getTradeResult()
            pushdata = {"stginfo": stginfo, "data": datas, "tradedetails": recordstr, "stockdetails":tdres.get("result_str")}
            func.setAccountKlineData(self.account_name, self.RUN_TYPE, pushdata)
            print('paint succ...')

        except Exception as e:
            print(e)
            traceback.print_exc()

if __name__ == "__main__":
    # Paint(account_name='BTC-RS2-TEST').start()
    account_name = 'BTC-RS2-TEST'

    # func.setAccountKlineData(account_name, 'VIRTUAL', {'aaa': 11})
    res = func.getAccountKlineData(account_name, 'VIRTUAL')
    print(res)
    # print(Paint.RUN_TYPE_STATIC)
    # func.setAccountProfit('dtest', 'virtual', 123, 22)
    # res = func.getAccountProfit('dtest', 'virtual')
    # print(res)
    # setprofit = cfg.getFetch().getObject('server.Data', 'setDatakey', ['profit', 12.0])
    # getprofit = cfg.getFetch().getFloat('server.Data', 'getDataByKey', ['profit'])
    # print(setprofit, getprofit)
