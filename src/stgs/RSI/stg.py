#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

'test for dev stg moudule'
__author__ = 'dpbtrader'
import sys
sys.path.append('../../')
from glc.DataStreamShipan import DataStreamShipan

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

class STG(DataStreamShipan):
    RUN_TYPE_STATIC = 'VIRTUAL'
    def __init__(self, account_name):
        self.midcresult = {"mc": 0, "mcMax": 0, "mcMin": 0}
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
        self.initUsdtUint = float(self.config.get('set', 'INIT_USDT_UNIT'))
        self.OVERSELL = float(self.config.get('trade', 'OVERSELL'))
        self.OVERBUY = float(self.config.get('trade', 'OVERBUY'))
        self.ENABLE_WINCOVER = self.config.get('trade', 'ENABLE_WINCOVER')
        self.WINCOVER = float(self.config.get('trade', 'WINCOVER'))
        self.LEVEL_POINT = float(self.config.get('trade', 'LEVEL_POINT'))
        super().__init__(account_name)

    def data_handler(self, data):
        tools.checkMainProcessStatusAndExit()
        # todos

    ## RSI计算公式
    # RSI = 100 – 100 / (1 + RS)
    # RS = Relative Strength = AvgU / AvgD
    # AvgU = 在最后N个bar里所有向上移动（涨了多少）的平均值
    # AvgD = 在最后N个bar里所有向下移动（跌了多少）的平均值
    # N = RSI周期
    def getRsi(self, datas):
        lengthdata = len(datas)
        # print('length', lengthdata)
        moveRow = datas[0]
        avgU = 0
        avgD = 0
        for i in range(lengthdata):
            if i > 0:
                currentRow = datas[i]
                if currentRow['close'] > moveRow['close']:
                    avgU = avgU + (currentRow['close'] - moveRow['close'])
                elif currentRow['close'] < moveRow['close']:
                    avgD = avgD + (moveRow['close'] - currentRow['close'])
                moveRow = currentRow

        # RSI = 100 – [100 / (1 + (Average of Upward Price Change / Average of Downward Price Change))]
        if avgD == 0:
            rsi = 100
        else:
            rs = avgU / avgD
            # rsi0 = 100 - (100 / (1 + rs))
            rsi = 100 * rs / (1 + rs)
        return round(rsi, 2)

    def checkOrderInTradeTime(self, nowtime, checkprice):
        allorders = self.trade.orders
        if len(allorders) > 0:
            lastorder = allorders[-1]
            lastOrderTime = func.transF1DateToTime(lastorder['time'])
            if nowtime - lastOrderTime > int(self.config.get('trade', 'ORDER_S_TIME')):
                if self.LEVEL_POINT > 0:
                    firstp = float(lastorder['price'])
                    checkprice = float(checkprice)
                    if firstp > checkprice:
                        checkp = (firstp - checkprice) / firstp * 100
                        # print('checkp1', checkp)
                        return True if checkp >= self.LEVEL_POINT else False
                    elif firstp < checkprice:
                        checkp = (checkprice - firstp) / firstp * 100
                        # print('checkp2', checkp)
                        return True if checkp >= self.LEVEL_POINT else False
                    else:
                        return False
                return True
            else:
                return False
        else:
            return True

    def stg(self):
        print('some thing....')

    def tick_data(self, row, datashape):
        trade = self.trade
        lastdata = datashape[-1]
        timedate = func.transTimeToTimedate(row['time'], isUTC=False)
        rsi = self.getRsi(datashape)
        extra = {}
        extra['name'] = 'rsi'
        extra['rsi'] = rsi
        extra['showtime'] = func.transTimeToTimedateF1(row['time'])
        totalprofit = self.trade.getTotalProfitFromRecord()
        extra['profit'] = totalprofit
        extra['maxusdt'] = self.trade.midcresult['mcMax']

        if rsi < self.OVERSELL:
            res = trade.getTradeResult()
            # print(res)
            if res is not None and res['opt'] == 'sell':
                if self.ENABLE_WINCOVER == 'no':
                    trade.cover(price=lastdata['close'], timedate=timedate, rsi=rsi, msg='平空仓')
                    extra['tradeopt'] = 'cover_sell'
                else:
                    if self.ENABLE_WINCOVER == 'yes' and res.get('profit') > self.WINCOVER:
                        trade.cover(price=lastdata['close'], timedate=timedate, rsi=rsi, msg='平空仓')
                        extra['tradeopt'] = 'cover_sell'
                    else:
                        if self.checkOrderInTradeTime(row['time'], row['close']):
                            # 减仓
                            trade.addOrder(optype='buy',
                                           currency=self.initUsdtUint,
                                           price=lastdata['close'],
                                           timedate=func.transTimeToTimedate(row['time'], isUTC=False), rsi=rsi,
                                           msg="减仓")
                            extra['tradeopt'] = 'buy'

            else:
                if self.checkOrderInTradeTime(row['time'], row['close']):
                    trade.addOrder(optype='buy',
                                   currency=self.initUsdtUint,
                                   price=lastdata['close'],
                                   timedate=func.transTimeToTimedate(row['time'], isUTC=False), rsi=rsi)

                    extra['tradeopt'] = 'buy'


        elif rsi > self.OVERBUY:
            res = trade.getTradeResult()
            if res is not None and res['opt'] == 'buy':
                if self.ENABLE_WINCOVER == 'no':
                    trade.cover(price=lastdata['close'], timedate=timedate, rsi=rsi, msg='平多仓')
                    extra['tradeopt'] = 'cover_buy'
                else:
                    if self.ENABLE_WINCOVER == 'yes' and res.get('profit') > self.WINCOVER:
                        trade.cover(price=lastdata['close'], timedate=timedate, rsi=rsi, msg='平多仓')
                        extra['tradeopt'] = 'cover_buy'
                    else:
                        if self.checkOrderInTradeTime(row['time'], row['close']):
                            # 减仓
                            trade.addOrder(optype='sell',
                                           currency=self.initUsdtUint,
                                           price=lastdata['close'],
                                           timedate=func.transTimeToTimedate(row['time'], isUTC=False), rsi=rsi,
                                           msg="减仓")
                            extra['tradeopt'] = 'sell'
            else:
                if self.checkOrderInTradeTime(row['time'], row['close']):
                    # 加仓
                    trade.addOrder(optype='sell',
                                   currency=self.initUsdtUint,
                                   price=lastdata['close'],
                                   timedate=func.transTimeToTimedate(row['time'], isUTC=False), rsi=rsi)
                    extra['tradeopt'] = 'sell'

        if self.config.get('set', 'PRINT_RUNTIME_TRACE') == 'yes':
            ptimef1 = func.transTimeToTimedateF1(row['time'], isUTC=False)
            trade.dumpTrade(ptime=ptimef1, price=row['close'])

        return extra

if __name__ == "__main__":

    td = Trade('btcTUSD')
    res = td.get_accounts()
    print(res)
    exit()
    # Paint('dtest2').start()

    # print(Paint.RUN_TYPE_STATIC)
    # func.setAccountProfit('dtest', 'virtual', 123, 22)
    # res = func.getAccountProfit('dtest', 'virtual')
    # print(res)
    # setprofit = cfg.getFetch().getObject('server.Data', 'setDatakey', ['profit', 12.0])
    # getprofit = cfg.getFetch().getFloat('server.Data', 'getDataByKey', ['profit'])
    # print(setprofit, getprofit)
