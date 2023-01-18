#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

'trade moudule'
__author__ = 'dpbtrader'

import time
import datetime
import json
import pandas as pd
import func
from decimal import Decimal
try:
    import thread
except ImportError:
    import _thread as thread
import cfg
import random
from gateAPI import GateIO
from okex.lever_api import LeverAPI
from binance.spot import Spot as Client

class Trade:

    def __init__(self, account_name):
        key_cfg = cfg.getAccountCfg(account_name, stg=False)
        self.config = config = key_cfg

        # config = cfg.getCfg()

        self.startTime = time.time()
        self.TRADE_BROKER_TYPE = config.get('set', 'TRADE_BROKER_TYPE')
        self.SHIPAN_ENABLE = config.get('set', 'SHIPAN_ENABLE')
        self.SHIPAN_TYPE = config.get('set', 'SHIPAN_TYPE')

        nowHour = datetime.datetime.now().strftime('%Y%m%d%H')

        ## 填写 apiKey APISECRET
        apiKey = config.get('set', 'APPID')
        secretKey = config.get('set', 'APIKEY')

        self.orders = cfg.getAccountLatestOrders(account_name=account_name)
        self.midcresult = {"mc": 0, "mcMax": 0, "mcMin": 0}

        if self.TRADE_BROKER_TYPE == 'gateio':
            print('TRADE_BROKER_TYPE not support')

            # API_QUERY_URL = config.get('gateio', 'API_QUERY_URL')
            # API_TRADE_URL = config.get('gateio', 'API_TRADE_URL')
            # self.gate_trade = GateIO(API_TRADE_URL, apiKey, secretKey)
        elif self.TRADE_BROKER_TYPE == 'binance':
            proxies = None
            if config.has_option('set', 'httpProxies'):
                httpProxies = config.get('set', 'httpProxies')
                if len(httpProxies) > 0:
                    proxies = {'https': httpProxies}
            self.gate_trade = Client(key = apiKey, secret = secretKey, proxies = proxies)
        else:
            # passphrase = config.get(self.TRADE_BROKER_TYPE, 'passphrase')
            # self.gate_trade = LeverAPI(apiKey, secretKey, passphrase, True)
            print('TRADE_BROKER_TYPE not support')

    def sell(self, usdT = 5, price = None, trytime = 3, tradeVariety = 'ETH-USDT'):
        if self.SHIPAN_ENABLE != 'yes':
            print("SHIPAN DISABLED")
            return False
        if self.SHIPAN_TYPE == 'VIRTUAL':
            order = {"deal_money": usdT, "filledRate": price, "optype": "sell"}
            return order

        if self.TRADE_BROKER_TYPE == 'gateio':
            return self.sell_gate(usdT, price, trytime, tradeVariety)
        elif self.TRADE_BROKER_TYPE == 'binance':
            return self.trade_binance('SELL', usdT, price, trytime, tradeVariety)
        else:
            return self.sell_okex(usdT, price, trytime, tradeVariety)

    def buy(self, usdT = 5, price = None, trytime = 3, tradeVariety = 'ETH-USDT'):
        if self.SHIPAN_ENABLE != 'yes':
            print("SHIPAN DISABLED")
            return False

        if self.SHIPAN_TYPE == 'VIRTUAL':
            order = {"deal_money": usdT, "filledRate": price, "optype": "buy"}
            return order

        if self.TRADE_BROKER_TYPE == 'gateio':
            return self.buy_gate(usdT, price, trytime, tradeVariety)
        elif self.TRADE_BROKER_TYPE == 'binance':
            return self.trade_binance('BUY', usdT, price, trytime, tradeVariety)
        else:
            return self.buy_okex(usdT, price, trytime, tradeVariety)


    def sell_okex(self, usdT = 5, price = None, trytime = 3, tradeVariety = 'ETH-USDT'):
        cpair = 'eth-usdt'
        if tradeVariety == 'ETH-USDT':
            cpair = 'eth-usdt'
        elif tradeVariety == 'EOS-USDT':
            cpair = 'eos-usdt'
        elif tradeVariety == 'BTC-USDT':
            cpair = 'btc-usdt'

        print("cpair %s" % cpair, "tradeVariety %s" % tradeVariety)
        if trytime == 0:
            return None

        if trytime == 1:
            price = Decimal(price) - Decimal(price) * Decimal('0.0018')
            pass

        amount = "%.6f" % (Decimal(usdT) / Decimal(price))
        print(price, amount, trytime, 'sell')
        try:
            sell_result = self.gate_trade.sell(price, amount, cpair = cpair)
        except Exception as e:
            print("sell json load err:")
            print(e)
            return None
        # deal_money filledRate deal_stock result
        print("sell_order_result", sell_result)

        if sell_result.get('result') == 'false':
            print("data error")
            print(sell_result)
            return None
        else:

            if float(sell_result.get('deal_stock')) > 0:
                print(sell_result)
                return sell_result
            else:
                time.sleep(0.1)
                return self.sell(usdT, price, trytime - 1, tradeVariety = tradeVariety)


    def sell_gate(self, usdT = 5, price = None, trytime = 5, tradeVariety = 'ETH-USDT'):
        if trytime == 0:
            return None

        if trytime == 1:
            price = Decimal(price) - Decimal(price) * Decimal('0.0018')

        cpair = 'eth_usdt'
        if tradeVariety == 'ETH-USDT':
            cpair = 'eth_usdt'
        elif tradeVariety == 'EOS-USDT':
            cpair = 'eos_usdt'
        elif tradeVariety == 'BTC-USDT':
            cpair = 'btc_usdt'

        amount = "%.4f" % (Decimal(usdT) / Decimal(price))
        print(price, amount, trytime, 'sell')
        try:
            sell_result = json.loads(self.gate_trade.sell(cpair, price, amount))
        except Exception as e:
            print("sell json load err:")
            print(e)
            return None
        print(sell_result)

        if sell_result.get('result') == 'false':
            print("data error")
            print(sell_result)
            return None
        else:

            if float(sell_result.get('filledAmount')) > 0:
                deal_stock = float(sell_result.get('filledAmount'))
                deal_price = float(sell_result.get('filledRate'))
                deal_money = deal_stock * deal_price
                return {'result': 'true', 'deal_stock': deal_stock, 'deal_money': deal_money, 'filledRate': deal_price}

            else:
                time.sleep(0.1)
                return self.sell(usdT, price, trytime - 1, tradeVariety = tradeVariety)

    def buy_okex(self, usdT = 5, price = None, trytime = 3, tradeVariety = 'ETH-USDT'):
        cpair = 'eth-usdt'
        if tradeVariety == 'ETH-USDT':
            cpair = 'eth-usdt'
        elif tradeVariety == 'EOS-USDT':
            cpair = 'eos-usdt'
        elif tradeVariety == 'BTC-USDT':
            cpair = 'btc-usdt'

        print('cpair', cpair)

        if trytime == 0:
            return None
        if trytime == 1:
            price = Decimal(price) +  Decimal(price) * Decimal('0.0018')
            pass

        amount = "%.6f" % (Decimal(usdT) / Decimal(price))
        print(price, amount, trytime , 'buy')
        try:
            buy_result = self.gate_trade.buy(price, amount, cpair = cpair)
        except Exception as e:
            print("buy json load err:")
            print(e)
            return None
        print("buy_order_result", buy_result)

        if buy_result.get('result') == 'false':
            print("data error")
            print(buy_result)
            return None
        else:
            if float(buy_result.get('deal_stock')) > 0:
                print(buy_result)
                return buy_result
            else:
                time.sleep(0.1)
                return self.buy(usdT, price, trytime - 1, tradeVariety = tradeVariety)

    def buy_gate(self, usdT = 5, price = None, trytime = 5, tradeVariety = 'ETH-USDT'):
        if trytime == 0:
            return None
        if trytime == 1:
            price = Decimal(price) +  Decimal(price) * Decimal('0.0018')

        cpair = 'eth_usdt'
        if tradeVariety == 'ETH-USDT':
            cpair = 'eth_usdt'
        elif tradeVariety == 'EOS-USDT':
            cpair = 'eos_usdt'
        elif tradeVariety == 'BTC-USDT':
            cpair = 'btc_usdt'

        amount = "%.4f" % (Decimal(usdT) / Decimal(price))
        print(price, amount, trytime , 'buy')
        try:
            buy_result = json.loads(self.gate_trade.buy(cpair, price, amount))
        except Exception as e:
            print("buy json load err:")
            print(e)
            return None
        # print(buy_result)
        if buy_result.get('result') == 'false':
            print("data error")
            print(buy_result)
            return None
        else:
            if float(buy_result.get('filledAmount')) > 0:
                deal_stock = float(buy_result.get('filledAmount'))
                deal_price = float(buy_result.get('filledRate'))
                deal_money = deal_stock * deal_price
                return {'result': 'true', 'deal_stock': deal_stock, 'deal_money': deal_money, 'filledRate': deal_price}
            else:
                time.sleep(0.1)
                return self.buy(usdT, price, trytime - 1, tradeVariety = tradeVariety)

    def trade_binance(self, opt, usdT, price , trytime, tradeVariety):


        cpair = tradeVariety.upper().replace("-", "")
        print('cpair', cpair)

        if trytime == 0:
            return None

        if trytime == 1:
            if opt == 'BUY':
                price = Decimal(price) + Decimal(price) * Decimal('0.0018')
            else:
                price = Decimal(price) - Decimal(price) * Decimal('0.0018')

        price = Decimal(price).quantize(Decimal('0.00'))

        double_format = "%.6f"
        if cpair == 'BTCUSDT':
            double_format = "%.5f"
        amount = double_format % (Decimal(usdT) / Decimal(price))

        print(price, amount, trytime , opt)
        try:
            # asset borrow repay
            user_assets = self.gate_trade.margin_account()
            df = pd.DataFrame(user_assets['userAssets'])
            df.index = df['asset']

            asset_name = cpair[0:-4]
            current_asset = df.loc[asset_name]
            usdt_asset = df.loc['USDT']

            if opt == 'BUY':
                if float(usdt_asset['free']) < usdT:
                    borrow_usdt = self.gate_trade.margin_borrow('USDT', usdT)
                    print("need borrow usdt:", borrow_usdt)
            else:
                if float(current_asset['free']) < float(amount):
                    borrow_asset = self.gate_trade.margin_borrow(asset_name, amount)
                    print("need borrow asset", borrow_asset)
        except Exception as e:
            print("binance outer api error")
            print(e)
            return None

        try:
            params = {
                'symbol': cpair,
                'side': opt, # SELL OR BUY
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': amount,
                'price': price
            }

            print(params)
            new_order = self.gate_trade.new_margin_order(**params)

            print(new_order)
        except Exception as e:
            print("opt load err:")
            print(e)
            return None
        print("opt_order_result", params, new_order)
        if new_order.get('status') == 'FILLED':
            print('opt succ', new_order)
            order = {"deal_money": new_order['cummulativeQuoteQty'], "filledRate": new_order['price']}

            try:
                repay_asset = 'USDT'
                borrow_num = float(usdt_asset['borrowed'])
                free_num = float(usdt_asset['free'])

                if opt == 'BUY':
                    repay_asset = asset_name
                    borrow_num = float(current_asset['borrowed'])
                    free_num = float(current_asset['free'])

                if free_num > borrow_num:
                    repay_result = self.gate_trade.margin_repay(repay_asset, borrow_num)
                    print(repay_result)

            except Exception as e:
                print("repay error", e)

            return order
        else:
            time.sleep(random.randint(1, 5))
            open_orders = self.gate_trade.margin_open_orders()
            if len(open_orders) > 0:
                print("clear orders")
                try:
                    self.gate_trade.margin_open_orders_cancellation(cpair)
                    if opt == 'BUY':
                        return self.buy(usdT, price, trytime - 1, tradeVariety = tradeVariety)
                    else:
                        return self.sell(usdT, price, trytime - 1, tradeVariety = tradeVariety)
                except Exception as e:
                    print(e, str(e).find('Unknown order sent') > 0)
                    if str(e).find('Unknown order sent') > 0:
                        print("cancel time trade")
                        show_order = self.gate_trade.margin_order(symbol = cpair, orderId = new_order['orderId'])
                        print(show_order)
                        order = {"deal_money": show_order['cummulativeQuoteQty'], "filledRate": show_order['price']}
                        return order
                    else:
                        return None
            else:
                print("empty time trade")
                show_order = self.gate_trade.margin_order(symbol = cpair, orderId = new_order['orderId'])
                print(show_order)

                order = {"deal_money": show_order['cummulativeQuoteQty'], "filledRate": show_order['price']}
                return order


    def pingc(self, timedate, price, forcepc = False):
        price = float(price)
        for i in range(len(self.orders)):
            if self.orders[i]['complete'] == 1:
                continue
            self.orders[i]['currency'] = float(self.orders[i]['currency'])
            absVal = abs(price - float(self.orders[i]['price']))
            absP = absVal / price
            if forcepc == True:
                self.orders[i]['complete'] = 1
            else:
                self.orders[i]['complete'] = 0

            self.orders[i]['pprice'] = price
            self.orders[i]['ptimedate'] = func.transTimedateToDate(timedate)
            self.orders[i]['pt'] = absP

            if self.orders[i]['type'] == 'sell':
                if float(self.orders[i]['price']) > price:
                    self.orders[i]['suc'] = 1
                    self.orders[i]['profit'] = (float(self.orders[i]['price']) - price) / price * self.orders[i]['currency']
                else:
                    self.orders[i]['suc'] = 2
                    self.orders[i]['profit'] = -(price - float(self.orders[i]['price'])) / float(self.orders[i]['price']) * self.orders[i]['currency']
            else:
                if float(self.orders[i]['price']) < price:
                    self.orders[i]['suc'] = 1
                    self.orders[i]['profit'] = (price - float(self.orders[i]['price'])) / float(self.orders[i]['price']) * self.orders[i]['currency']
                    (float(self.orders[i]['price']) - price) / price * self.orders[i]['currency']
                else:
                    self.orders[i]['suc'] = 2
                    self.orders[i]['profit'] = -(float(self.orders[i]['price']) - price) / price * self.orders[i]['currency']

            self.orders[i]['price'] = Decimal(self.orders[i]['price']).quantize(Decimal('0.0000'))
            self.orders[i]['pt'] = Decimal(absP).quantize(Decimal('0.00000'))
            self.orders[i]['profit'] = Decimal(self.orders[i]['profit']).quantize(Decimal('0.000'))
            self.orders[i]['currency'] = Decimal(self.orders[i]['currency']).quantize(Decimal('0.0000'))


    def getTradeResult(self, timedate = None, price = None):
        result_orders = self.orders
        # if ispc:
        #     if len(self.orders) > 0:
        #         result_orders = self.orders[0:-1]

        if len(result_orders) > 0:
            if timedate is None:
                lastorder = result_orders[-1]
                timedate = func.transF1ToTimedateF2(lastorder['timedate'])
                price = lastorder['price']
            self.pingc(timedate, price)

        df = pd.DataFrame(result_orders)

        if len(df) == 0:
            return None

        showStr = ""
        dataListStr = ""

        opt = 'none'
        amount = 0
        open_price = 0
        profit = 0
        open_date = 'empty'

        df['complete'] = df['complete'].astype(float)

        df = df.loc[df.complete == 0]

        if len(df) > 0:
            open_date = df.loc[df.index[0]]['timedate']

            dataListStr = func.printDataFrame(df)
            price = float(price)
            df_succ = df.loc[df.suc == 1]
            df_fail = df.loc[df.suc == 2]

            df_sell = df.loc[df.type == 'sell']
            df_buy = df.loc[df.type == 'buy']

            Ebpc = 0
            Espc = 0

            Ebc = 0
            Esc = 0
            for gk in range(len(df)):
                dfrow = df.loc[df.index[gk]]
                if dfrow['type'] == 'buy':
                    Ebpc = Ebpc + float(dfrow['currency']) / float(dfrow['price'])
                    Ebc = Ebc + float(dfrow['currency'])
                else:
                    Espc = Espc + float(dfrow['currency']) / float(dfrow['price'])
                    Esc = Esc + float(dfrow['currency'])

            Eamount = abs(Ebpc + (-Espc))

            Ecostusd =  abs(Ebc - Esc)

            self.midcresult['mc'] = (Ecostusd +  self.midcresult['mc']) / 2

            if Ecostusd > self.midcresult['mcMax']:
                self.midcresult['mcMax'] = Ecostusd

            if Ecostusd < self.midcresult['mcMin']:
                self.midcresult['mcMin'] = Ecostusd

            Eshow = ''
            opt = "none"
            amount = Eamount
            open_price = 0

            amount = float("%.5f" % amount)

            c_profit = df['profit'].astype('float64').sum()
            profit = c_profit

            if Ebc - Esc > 0:
                open_price = (Ebc - Esc) / amount
                Eshow = "做多:数量{:.5f}，金额{:.2f}，成本价{:.4f}".format(amount, Ebc - Esc, open_price)
                opt = "buy"

            elif Ebc - Esc < 0:
                open_price = (Esc - Ebc) / amount
                Eshow = "做空:数量{:.5f}，金额{:.2f}，成本价{:.4f}".format(amount, Esc - Ebc, open_price)
                opt = "sell"
            else:
                pass

            r_transfer = c_profit / self.midcresult['mc']

            # print('c_profit', c_profit)
            # print('midcresult', self.midcresult['mc'])

            showStr = showStr + ("最大占用 %.4f" % self.midcresult['mcMax']) + "\n"
            # showStr = showStr + ("最小占用 %.2f" % self.midcresult['mcMin']) + "\n"

            showStr = showStr + ("转化率 %.5f" % (r_transfer * 100)) + "\n"

            showStr = showStr + ("总体盈利 %.5f" % c_profit) + "\n"
            showStr = showStr + ("总单数 %d , 多单 %d, 空单 %d" % (len(df), len(df_buy), len(df_sell))) + "\n"

            showStr = showStr + ("当前价格 %.2f" % price) + "\n"
            showStr = showStr + ("方向 %s" % Eshow) + "\n"

        result_str = dataListStr + "\n" + showStr

        print(dataListStr, showStr)

        usdt_amount = "%.2f" % (amount * open_price)
        return {"result_str": result_str, "opt": opt, "amount": "%.5f" % amount, "usdt_amount": usdt_amount, "open_price": "%.2f" % open_price, "profit": "%.5f" % profit, "open_date": open_date}


if __name__ == "__main__":
    t = Trade('dtest').getTradeResult()
    print(t)
    # res = t.sell(1, 148.3)
    #  usdT = 5, price = None, trytime = 3, tradeVariety = 'ETH-USDT'
    # binance btc test for sell min amount > : 0.00017 4$ , for buy amount > : 0.001 25$ , if low get  'MIN_NOTIONAL' msg
    # res = t.buy(usdT = 25, price = 5000, trytime = 3, tradeVariety = 'BTC-USDT')
    # #res = t.sell(10, 9600, tradeVariety = 'BTC-USDT')
    # print(res)

