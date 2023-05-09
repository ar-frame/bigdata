#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

'trade moudule'
__author__ = 'dpbtrader'

import copy
import os
import re
import time
import datetime
import json
import pandas as pd
import func
from decimal import Decimal

import tools

try:
    import thread
except ImportError:
    import _thread as thread
import cfg
import random
from gateAPI import GateIO
from okex.lever_api import LeverAPI
from binance.spot import Spot as Client
from dbconn import MongoDB


class Trade:

    def __init__(self, account_name):
        key_cfg = cfg.getAccountCfg(account_name, stg=False)
        self.config = config = key_cfg
        self.account_name = account_name
        self.startTime = time.time()
        self.TRADE_BROKER_TYPE = config.get('set', 'TRADE_BROKER_TYPE')
        self.SHIPAN_ENABLE = config.get('set', 'SHIPAN_ENABLE')
        self.SHIPAN_TYPE = config.get('set', 'SHIPAN_TYPE')
        # self.RUN_TYPE = 'VIRTUAL'  # 手动触发回测

        self.stg_config = stg_cfg = cfg.getAccountCfg(account_name, stg=True)
        self.tradeVariety = self.stg_config.get('set', 'TRADE_VARIETY')

        mongo_store = cfg.getMongo('store')
        self.db_mongo_store = MongoDB(mongo_store.get('DB'),
                                      'orders_' + func.formatStoreName(self.tradeVariety) + '_' + self.account_name,
                                      mongo_store.get('DB_HOST'), mongo_store.get('DB_USER'),
                                      mongo_store.get('DB_PASS'), mongo_store.get('DB_PORT'))

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
            if cfg.getCfg().has_option('set', 'httpproxies'):
                httpProxies = cfg.getCfg().get('set', 'httpproxies')
                if len(httpProxies) > 0:
                    proxies = {'https': httpProxies}
            self.gate_trade = Client(apiKey, secretKey, proxies=proxies)
        else:
            # passphrase = config.get(self.TRADE_BROKER_TYPE, 'passphrase')
            # self.gate_trade = LeverAPI(apiKey, secretKey, passphrase, True)
            print('TRADE_BROKER_TYPE not support')

    def checkIsRealTrading(self):
        if self.SHIPAN_ENABLE != 'yes':
            return False
        if self.SHIPAN_TYPE == 'VIRTUAL':
            return False
        return tools.checkAccountProcessIsRun(self.account_name, shipan=True)

    def sell(self, usdT=5, price=None, trytime=3, tradeVariety='ETH-USDT'):
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

    def buy(self, usdT=5, price=None, trytime=3, tradeVariety='ETH-USDT'):
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

    def sell_okex(self, usdT=5, price=None, trytime=3, tradeVariety='ETH-USDT'):
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
            sell_result = self.gate_trade.sell(price, amount, cpair=cpair)
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
                return self.sell(usdT, price, trytime - 1, tradeVariety=tradeVariety)

    def sell_gate(self, usdT=5, price=None, trytime=5, tradeVariety='ETH-USDT'):
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
                return self.sell(usdT, price, trytime - 1, tradeVariety=tradeVariety)

    def buy_okex(self, usdT=5, price=None, trytime=3, tradeVariety='ETH-USDT'):
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
            price = Decimal(price) + Decimal(price) * Decimal('0.0018')
            pass

        amount = "%.6f" % (Decimal(usdT) / Decimal(price))
        print(price, amount, trytime, 'buy')
        try:
            buy_result = self.gate_trade.buy(price, amount, cpair=cpair)
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
                return self.buy(usdT, price, trytime - 1, tradeVariety=tradeVariety)

    def buy_gate(self, usdT=5, price=None, trytime=5, tradeVariety='ETH-USDT'):
        if trytime == 0:
            return None
        if trytime == 1:
            price = Decimal(price) + Decimal(price) * Decimal('0.0018')

        cpair = 'eth_usdt'
        if tradeVariety == 'ETH-USDT':
            cpair = 'eth_usdt'
        elif tradeVariety == 'EOS-USDT':
            cpair = 'eos_usdt'
        elif tradeVariety == 'BTC-USDT':
            cpair = 'btc_usdt'

        amount = "%.4f" % (Decimal(usdT) / Decimal(price))
        print(price, amount, trytime, 'buy')
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
                return self.buy(usdT, price, trytime - 1, tradeVariety=tradeVariety)

    def getFixNum(self, rules: str):
        return rules.find('1') - 1

    def getKline(self):
        cpair = func.formatSymbolName(self.tradeVariety)
        try:
            klines = self.gate_trade.klines(symbol=cpair, interval='1s', limit=1)
            if klines and len(klines) > 0:
                data = klines[0]
                totalvol = float(data[5]);
                totalbvol = float(data[-3])
                totalsvol = totalvol - totalbvol
                if totalsvol > totalbvol:
                    opt = 'sell'
                else:
                    opt = 'buy'
                dataobj = {
                    "time": int(int(data[0]) / 1000),
                    "open": float(data[1]),
                    "high": float(data[2]),
                    "low": float(data[3]),
                    "close": float(data[4]),
                    "vol": float(totalvol),
                    "opt": opt,
                    "totalbvol": float(totalbvol),
                    "tradecount": int(data[-4])
                }

                avg = dataobj['high'] - (dataobj['high'] - dataobj['low']) / 2
                dataobj['avg'] = avg
                return dataobj
        except Exception as e:
            print('get klines e:', e)
            return None

    def getTickPirce(self):
        cpair = func.formatSymbolName(self.tradeVariety)
        try:
            tickprice = self.gate_trade.ticker_price(symbol=cpair)
            print('tickprice', tickprice)
            return float(tickprice['price'])
        except Exception as e:
            print('get tickprice e:', e)
            return None

    def get_accounts(self):
        cpair = func.formatSymbolName(self.tradeVariety)
        user_assets = self.gate_trade.isolated_margin_account(symbols=cpair, recvWindow=20000)
        base_asset = user_assets['assets'][0]['baseAsset']
        quote_asset = user_assets['assets'][0]['quoteAsset']
        price = float(user_assets['assets'][0]['indexPrice'])

        quote_asset['free'] = float(quote_asset['free'])
        quote_asset['interest'] = float(quote_asset['interest'])
        quote_asset['borrowed'] = float(quote_asset['borrowed'])

        base_asset['free'] = float(base_asset['free'])
        base_asset['interest'] = float(base_asset['interest'])
        base_asset['borrowed'] = float(base_asset['borrowed'])

        real_total_assetnum = (quote_asset['free'] - quote_asset['interest'] - quote_asset['borrowed'])\
                              + (base_asset['free'] - base_asset['interest'] - base_asset['borrowed']) * price

        return {"base_asset": base_asset, "quote_asset": quote_asset, "real_total_assetnum": real_total_assetnum, \
                "margin_level": user_assets['assets'][0]['marginLevel']}

    def trade_binance(self, opt, usdT, price, trytime, tradeVariety):
        # cpair = tradeVariety.upper().replace("-", "")
        cpair = func.formatSymbolName(tradeVariety)
        # exit()

        # orderid = '781119569'
        # show_order = self.gate_trade.margin_order(symbol=cpair, orderId=orderid,
        #                                           isIsolated='TRUE')

        # deal_price = float(show_order['cummulativeQuoteQty']) / float(show_order['executedQty'])
        # print('order deal_price e:', deal_price)
        #
        # print(show_order)
        # exit()

        print('trade_binance cpair', cpair)
        if trytime == 0:
            return None
        if trytime == 1:
            if opt == 'BUY':
                price = Decimal(price) + Decimal(price) * Decimal('0.0018')
            else:
                price = Decimal(price) - Decimal(price) * Decimal('0.0018')
        # price = Decimal(price).quantize(Decimal('0.00000'))
        try:
            exchange_info = self.gate_trade.exchange_info(symbol=cpair)
            print('exchangeinfo', exchange_info)
            price_rules = exchange_info['symbols'][0]['filters'][0]
            minprice = float(price_rules['minPrice'])
            maxprice = float(price_rules['maxPrice'])
            ticksize = price_rules['tickSize']

            lotsize_rules = exchange_info['symbols'][0]['filters'][1]
            # {'filterType': 'LOT_SIZE', 'minQty': '0.10000000', 'maxQty': '9000000.00000000', 'stepSize': '0.10000000'}
            minqty = float(lotsize_rules['minQty'])
            maxqty = float(lotsize_rules['maxQty'])
            stepsize = lotsize_rules['stepSize']

            pricefixnum = self.getFixNum(ticksize)
            amountfixnum = self.getFixNum(stepsize)
            double_format = "%." + str(amountfixnum) + "f"
            price = ("%." + str(pricefixnum) + "f") % price
            price = float(price)

            amount = double_format % (Decimal(usdT) / Decimal(price))
            amount = float(amount)
            print(price, amount, trytime, opt)
            # asset borrow repay
            # user_assets = self.gate_trade.isolated_margin_account(symbols=cpair)
            # print('user ass', json.dumps(user_assets))

            user_assets = self.get_accounts()
            print('user ass', json.dumps(user_assets))
            base_asset = user_assets['base_asset']
            quote_asset = user_assets['quote_asset']
            print(base_asset, quote_asset)

            asset_name = base_asset['asset']
            quote_assetname = quote_asset['asset']

            base_assetnum = float(base_asset['free'])
            usdt_assetnum = float(quote_asset['free'])

            print('base_assetnum:', base_assetnum)
            print('usd_assetnum:', usdt_assetnum)

            if opt == 'BUY':
                if usdt_assetnum < usdT:
                    borrow_amount = usdT + 1
                    print("need borrow usdt:", quote_assetname, borrow_amount)
                    borrow_usdt = self.gate_trade.margin_borrow(asset=quote_assetname, amount=borrow_amount,
                                                                isIsolated='TRUE', symbol=cpair)
            else:
                if base_assetnum < float(amount):
                    print("need borrow asset", asset_name, amount)
                    borrow_asset = self.gate_trade.margin_borrow(asset=asset_name, amount=amount, isIsolated='TRUE',
                                                                 symbol=cpair)

        except Exception as e:
            print("binance outer api error")
            print(e)
            return None
        try:
            params = {
                'symbol': cpair,
                'side': opt,  # SELL OR BUY
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': amount,
                'price': price,
                'isIsolated': 'TRUE'
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
            origin_price = new_order['price']
            print('origin order price:', origin_price)
            deal_price = new_order['fills'][0]['price']
            print('order deal_price:', deal_price)
            order = {"deal_money": new_order['cummulativeQuoteQty'], "filledRate": deal_price}
            try:
                borrow_num = 0
                free_num = 0

                user_assets = self.get_accounts()
                print('user ass', json.dumps(user_assets))
                base_asset = user_assets['base_asset']
                quote_asset = user_assets['quote_asset']
                print(base_asset, quote_asset)

                if opt == 'BUY':
                    repay_asset = asset_name
                    borrow_num = float(base_asset['borrowed']) + float(base_asset['interest'])
                    free_num = float(base_asset['free'])
                elif opt == 'SELL':
                    repay_asset = quote_assetname
                    borrow_num = float(quote_asset['borrowed']) + float(quote_asset['interest'])
                    free_num = float(quote_asset['free'])

                if free_num > borrow_num:
                    repay_result = self.gate_trade.margin_repay(repay_asset, borrow_num, isIsolated='TRUE', symbol=cpair)
                    print('repay succ...', repay_result)

            except Exception as e:
                print("repay error----", e)
            return order
        else:
            time.sleep(random.randint(1, 5))
            open_orders = self.gate_trade.margin_open_orders(symbol=cpair, isIsolated='TRUE')
            if len(open_orders) > 0:
                print("clear orders")
                try:
                    self.gate_trade.margin_open_orders_cancellation(cpair, isIsolated='TRUE')
                    if opt == 'BUY':
                        return self.buy(usdT, price, trytime - 1, tradeVariety=tradeVariety)
                    else:
                        return self.sell(usdT, price, trytime - 1, tradeVariety=tradeVariety)
                except Exception as e:
                    print(e, str(e).find('Unknown order sent') > 0)
                    if str(e).find('Unknown order sent') > 0:
                        print("cancel time trade")
                        show_order = self.gate_trade.margin_order(symbol=cpair, orderId=new_order['orderId'],
                                                                  isIsolated='TRUE')

                        # orderid = '780671313'
                        print(show_order)

                        origin_price = show_order['price']
                        print('origin order price e:', origin_price)
                        deal_price = float(show_order['cummulativeQuoteQty']) / float(show_order['executedQty'])
                        print('order deal_price e:', deal_price)

                        order = {"deal_money": show_order['cummulativeQuoteQty'], "filledRate": deal_price}
                        return order
                    else:
                        return None
            else:
                print("empty time trade show order")
                show_order = self.gate_trade.margin_order(symbol=cpair, orderId=new_order['orderId'], isIsolated='TRUE')
                print('show order:', show_order)

                origin_price = show_order['price']
                print('origin order price else:', origin_price)
                deal_price = float(show_order['cummulativeQuoteQty']) / float(show_order['executedQty'])
                print('order deal_price else:', deal_price)

                order = {"deal_money": show_order['cummulativeQuoteQty'], "filledRate": deal_price}
                return order

    def pingc(self, ptime, price, forcepc=False):
        price = float(price)
        for i in range(len(self.orders)):
            if self.orders[i]['complete'] == 1:
                continue

            self.orders[i]['price'] = float(self.orders[i]['price'])
            self.orders[i]['currency'] = float(self.orders[i]['currency'])
            absVal = abs(price - float(self.orders[i]['price']))
            absP = absVal / (self.orders[i]['price'])

            if forcepc == True:
                self.orders[i]['complete'] = 1
            else:
                self.orders[i]['complete'] = 0

            self.orders[i]['pprice'] = price
            self.orders[i]['ptime'] = ptime
            self.orders[i]['pt'] = absP
            self.orders[i]['suc'] = 0

            if self.orders[i]['type'] == 'sell':
                if float(self.orders[i]['price']) > price:
                    self.orders[i]['suc'] = 1
                    self.orders[i]['profit'] = self.orders[i]['currency'] - (
                            self.orders[i]['currency'] / self.orders[i]['price'] * price)
                else:
                    paymoney = (self.orders[i]['currency'] / self.orders[i]['price'] * price - self.orders[i][
                        'currency'])
                    if paymoney > 0:
                        self.orders[i]['suc'] = 2
                        self.orders[i]['profit'] = -paymoney
                    else:
                        self.orders[i]['profit'] = 0
            else:
                if float(self.orders[i]['price']) < price:
                    self.orders[i]['suc'] = 1
                    self.orders[i]['profit'] = self.orders[i]['currency'] / self.orders[i]['price'] * price - \
                                               self.orders[i]['currency']
                else:
                    paymoney = self.orders[i]['currency'] - self.orders[i]['currency'] / self.orders[i]['price'] * price
                    if paymoney > 0:
                        self.orders[i]['suc'] = 2
                        self.orders[i]['profit'] = -paymoney
                    else:
                        self.orders[i]['profit'] = 0

            self.orders[i]['price'] = Decimal(self.orders[i]['price']).quantize(Decimal('0.00000'))
            self.orders[i]['pt'] = Decimal(absP).quantize(Decimal('0.00000'))
            self.orders[i]['profit'] = Decimal(self.orders[i]['profit']).quantize(Decimal('0.000'))
            self.orders[i]['currency'] = Decimal(self.orders[i]['currency']).quantize(Decimal('0.0000'))

        if forcepc == True:
            self.db_mongo_store.update(con={"complete": {"$eq": 0}}, data={"complete": 1})
            self.midcresult['mcMax'] = 0

    def dumpTrade(self, ptime=None, price=None):
        result_obj = self.getTradeResult(ptime, price)
        if result_obj is not None:
            print(result_obj.get("result_str"))

    def getTradeResult(self, ptime=None, price=None):
        result_orders = self.orders
        if len(result_orders) == 0:
            return None
        if ptime is None:
            ptime = result_orders[-1]['time']
        if price is None:
            price = result_orders[-1]['price']

        self.pingc(ptime, price)
        df = pd.DataFrame(self.orders)

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
            open_date = df.loc[df.index[0]]['time']
            dataListStr = func.printDataFrame(df)
            price = float(price)

            df_sell = df.loc[df.type == 'sell']
            df_buy = df.loc[df.type == 'buy']

            Ebamount = 0
            Esamount = 0

            Ebcurrency = 0
            Escurrency = 0

            Paymoney = 0
            Payamount = 0

            for gk in range(len(df)):
                dfrow = df.loc[df.index[gk]]
                if dfrow['type'] == 'buy':
                    Ebamount = Ebamount + float(dfrow['currency']) / float(dfrow['price'])
                    Ebcurrency = Ebcurrency + float(dfrow['currency'])
                else:
                    Esamount = Esamount + float(dfrow['currency']) / float(dfrow['price'])
                    Escurrency = Escurrency + float(dfrow['currency'])

            Paymoney = Ebcurrency - Escurrency
            Payamount = Esamount - Ebamount

            Eshow = ''
            opt = "none"
            amount = 0
            open_price = 0

            # print(Ebamount, Esamount)
            if Ebamount > 0 and Esamount > 0:
                if Ebamount > Esamount:
                    opt = 'buy'
                    amount = Ebamount - Esamount
                else:
                    opt = 'sell'
                    amount = Esamount - Ebamount
            else:
                if Ebamount > 0:
                    opt = 'buy'
                    amount = Ebamount
                elif Esamount > 0:
                    opt = 'sell'
                    amount = Esamount

            amount = float("%.9f" % amount)
            c_profit = df['profit'].astype('float64').sum()
            profit = c_profit

            # print(opt, amount, Paymoney)
            if amount * price > 1:
                if opt == 'buy':
                    open_price = Paymoney / amount
                    Eshow = "做多:持仓数量{:.5f}，负债金额{:.2f}，成本价{:.5f}".format(amount, Paymoney, open_price)

                elif opt == 'sell':
                    open_price = (Escurrency - Ebcurrency) / amount
                    Eshow = "做空:负债数量{:.5f}，持仓金额{:.2f}，成本价{:.5f}".format(amount, (Escurrency - Ebcurrency),
                                                                                     open_price)
                    opt = "sell"
                else:
                    pass

                Ecostusd = amount * price
                if Ecostusd > self.midcresult['mcMax']:
                    self.midcresult['mcMax'] = Ecostusd
            else:
                Eshow = "空仓"
                opt = 'none'

            # r_transfer = c_profit / (self.midcresult['mc'])

            # print('c_profit', c_profit)
            # print('midcresult', self.midcresult['mc'])

            showStr = showStr + ("最大占用 %.4f" % self.midcresult['mcMax']) + "\n"
            # showStr = showStr + ("最小占用 %.2f" % self.midcresult['mcMin']) + "\n"

            # showStr = showStr + ("转化率 %.5f" % (r_transfer * 100)) + "\n"

            showStr = showStr + ("总体盈利 %.5f" % c_profit) + "\n"
            showStr = showStr + ("总单数 %d , 多单 %d, 空单 %d" % (len(df), len(df_buy), len(df_sell))) + "\n"

            showStr = showStr + ("当前价格 %.5f" % price) + "\n"
            showStr = showStr + ("方向 %s" % Eshow) + "\n"

        result_str = dataListStr + "\n" + showStr

        usdt_amount = "%.2f" % (amount * open_price)
        return {"opt": opt, "amount": "%.9f" % amount, "usdt_amount": usdt_amount, "open_price": "%.5f" % open_price,
                "profit": float("%.5f" % profit), "open_date": open_date, "result_str": result_str}

    def addOrder(self, optype='buy', currency=0, price=None, timedate=None, **param):
        order = {}
        if self.RUN_TYPE == 'REAL':
            if optype == 'buy':
                optres = self.buy(currency, price, tradeVariety=self.tradeVariety)
            else:
                optres = self.sell(currency, price, tradeVariety=self.tradeVariety)

            if optres is not None:
                order = {"type": optype,
                         "currency": optres.get('deal_money'),
                         "price": optres.get('filledRate'),
                         "time": func.transTimedateToDate(timedate),
                         **param
                         }
                # mongo change the object value insert _Id
                morder = copy.copy(order)
                self.db_mongo_store.insert(morder)
            else:
                order = None
        else:
            order = {"type": optype, "currency": currency, "price": price, "time": func.transTimedateToDate(timedate),
                     **param}

        if order is not None:
            order['complete'] = 0
            if 'iscover' in param and param['iscover'] == True:
                self.logOrders(price=order['price'])
                self.orders.append(order)
                self.logOrders(price=order['price'])
            else:
                self.orders.append(order)

            if self.RUN_TYPE == 'REAL':
                self.storeRecentOrders()

        # profit = self.getTotalProfitFromRecord()
        # func.setAccountProfit(self.account_name, self.RUN_TYPE, tm = func.transTimedateToTime(timedate), profit=profit)

        return order

    def cover(self, price, timedate=None, **param):
        trade_result = self.getTradeResult()
        amount = float(trade_result.get("amount"))
        direct = str(trade_result.get("opt"))
        if amount > 0:
            if direct == 'buy':
                order = self.addOrder('sell', currency=amount * price, price=price, timedate=timedate, iscover=True,
                                      **param)
            else:
                order = self.addOrder('buy', currency=amount * price, price=price, timedate=timedate, iscover=True,
                                      **param)

            if order is not None and 'price' in order:
                if 'msg' in param:
                    msg = param['msg']
                else:
                    msg = ''
                self.orders = self.orders[0:-1]
                self.doPcRecordToResult(msg, price=order['price'])
                self.resetOrders()
            return True
        else:
            return False

    def resetOrders(self):
        self.orders = []
        self.midcresult['mcMax'] = 0

    def doPcRecordToResult(self, msg, price=None):
        trade_result = self.getTradeResult(price=price)
        # self.pingc(pointCode.get("timedate"), pointCode.get('price'), True)
        close_date = self.orders[-1]['time']
        if price is None:
            close_price = self.orders[-1]['price']
        else:
            close_price = price

        # print(trade_result, str(trade_result.get("open_price")),close_date, close_price)
        # exit()
        objs = { \
            "open_date": str(trade_result.get("open_date")), \
            "close_date": close_date, \
            "open_price": str(trade_result.get("open_price")), "close_price": close_price, \
            "usdt_amount": str(trade_result.get("usdt_amount")), "direct": str(trade_result.get("opt")), \
            "profit": str(trade_result.get("profit")), "msg": msg \
            }
        self.pcRecord(**objs)

    def pcRecord(self, open_date, close_date, open_price, close_price, usdt_amount, direct, profit, msg=""):

        variety = self.tradeVariety
        curpath = os.path.dirname(os.path.realpath(__file__))
        record_file = os.path.join(curpath,
                                   "data/" + "trade_record_" + self.RUN_TYPE + "_" + variety.lower().replace("-",
                                                                                                             "_") + "_" + self.account_name + "_" + ".csv")
        objs = {"variety": variety, "open_date": open_date, "close_date": close_date, "open_price": str(open_price),
                "close_price": str(close_price), "usdt_amount": str(usdt_amount), "direct": str(direct),
                "profit": str(profit), "msg": msg}
        head_title = ",".join(objs.keys())
        file_content = ''
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                f.close()
        except Exception as e:
            print('read e:', e)

        cal_profit = 0
        if len(file_content) > 0:
            file_content = file_content.strip()
            split_content = file_content.split("\n")
            for i in range(len(split_content)):
                if i > 0 and i < len(split_content) - 1:
                    row = split_content[i]
                    cal_profit = cal_profit + float(row.split(",")[-2])

            cal_profit = cal_profit + float(profit)
            last_row_str = "合计盈利：%.2f" % cal_profit

            del (split_content[-1])
            with open(record_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(split_content) + "\n")
                f.write(",".join(objs.values()))
                f.close()
        else:
            last_row_str = "合计盈利：%.2f" % float(profit)
            with open(record_file, 'w', encoding='utf-8') as f:
                f.write(head_title + "\n")
                f.write(",".join(objs.values()))
                f.close()

        with open(record_file, 'a', encoding='utf-8') as f:
            f.write("\n" + last_row_str + "\n")
            f.close()

    def getTotalProfitFromRecord(self, recordStr=False):
        curpath = os.path.dirname(os.path.realpath(__file__))
        record_file = os.path.join(curpath,
                                   "data/" + "trade_record_" + self.RUN_TYPE + "_" + self.tradeVariety.lower().replace(
                                       "-",
                                       "_") + "_" + self.account_name + "_" + ".csv")
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                file_content = f.read().strip()
                if recordStr == True:
                    return file_content

                if len(file_content) > 0:
                    mt = re.findall('合计盈利：(-?\d+\.?\d*)', file_content)
                    if len(mt) > 0:
                        return float(mt[0])
                    else:
                        return 0
        except Exception as e:
            return 0

    def getLogMark(self):
        return 'orders_' + self.RUN_TYPE + '_' + self.account_name

    def logOrders(self, price=None, isclear=False, msg=''):
        res = self.getTradeResult(price=price)
        if res is not None:
            result_str = res.get("result_str")
            msg = msg + result_str
        mark = self.getLogMark()
        cfg.write_log(mark, msg, isclear)

        # clear profit logs
        if isclear == True:
            if self.RUN_TYPE == 'VIRTUAL':
                variety = self.tradeVariety
                curpath = os.path.dirname(os.path.realpath(__file__))
                record_file = os.path.join(curpath,
                                           "data/" + "trade_record_" +
                                           self.RUN_TYPE + "_" + variety.lower().replace("-", "_") +
                                           "_" + self.account_name + "_" + ".csv")
                with open(record_file, 'w', encoding='utf-8') as f:
                    f.write("")

    def storeRecentOrders(self):
        orders = self.orders
        mark = 'orders_recent_' + self.RUN_TYPE + '_' + self.account_name
        func.writeOrderStore(mark, orders)

    def getRecentOrders(self):
        mark = 'orders_recent_' + self.RUN_TYPE + '_' + self.account_name
        return func.getOrderFromStoreFile(mark)


if __name__ == "__main__":
    res = func.getAccountProfit('dtest2', 'virtual')
    print(res)

    # res = t.sell(1, 148.3)
    #  usdT = 5, price = None, trytime = 3, tradeVariety = 'ETH-USDT'
    # binance btc test for sell min amount > : 0.00017 4$ , for buy amount > : 0.001 25$ , if low get  'MIN_NOTIONAL' msg
    # res = t.buy(usdT = 25, price = 5000, trytime = 3, tradeVariety = 'BTC-USDT')
    # #res = t.sell(10, 9600, tradeVariety = 'BTC-USDT')
    # print(res)
