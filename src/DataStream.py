#!/usr/bin/env python
import json
import logging
import time
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
# config_logging(logging, logging.DEBUG)
from dbconn import MongoDB
import func
import cfg
fetch = cfg.getFetch()

class DataStream:
    def __init__(self, account_name):
        key_cfg = cfg.getAccountCfg(account_name, stg=True)
        self.stgconfig = key_cfg
        self.symbol = self.stgconfig.get('set', 'TRADE_VARIETY').lower().replace('-', '').replace('_', '').strip()


    def on_error(self):
        print('on error 111...')

    def on_close(self):
        print('on on_close 111...')

    def start(self):
        self.my_client = SpotWebsocketStreamClient(on_message=self.message_handler,on_close=self.on_close, on_error=self.on_error, is_combined=True)
        # btcusdt
        self.my_client.kline(symbol=self.symbol, interval="1s")

    def stop(self):
        try:
            self.my_client.kline(
                symbol=self.symbol, interval="1s", action=SpotWebsocketStreamClient.ACTION_UNSUBSCRIBE
            )
            self.my_client.stop()
        except Exception as e:
            print('stop data web socket e', e)

    def data_handler(self, data):
        print('origin data..',  data)
        tradeVariety = self.symbol
        tradeVariety = func.formatSymbolName(tradeVariety)
        mark = tradeVariety.lower()
        mongo_store = cfg.getMongo('store')
        db_mongo_store = MongoDB(mongo_store.get('DB'), 'kline_' + mark, mongo_store.get('DB_HOST'),
                                 mongo_store.get('DB_USER'),
                                 mongo_store.get('DB_PASS'), mongo_store.get('DB_PORT'))

        db_mongo_store.insert(data)
        # fetch.getObject('server.Data', 'setDatakey', ['NEW_IN_DATA', data])
        # todo

    def message_handler(self, _, message):
        # print('message', type(message))
        msgobj = json.loads(message)
        # print(msgobj)
        # {
        #     "e": "kline", // 事件类型
        # "E": 1672515782136, // 事件时间
        # "s": "BNBBTC", // 交易对
        # "k": {
        #          "t": 1672515780000, // 这根K线的起始时间
        # "T": 1672515839999, // 这根K线的结束时间
        # "s": "BNBBTC", // 交易对
        # "i": "1m", // K线间隔
        # "f": 100, // 这根K线期间第一笔成交ID
        # "L": 200, // 这根K线期间末一笔成交ID
        # "o": "0.0010", // 这根K线期间第一笔成交价
        # "c": "0.0020", // 这根K线期间末一笔成交价
        # "h": "0.0025", // 这根K线期间最高成交价
        # "l": "0.0015", // 这根K线期间最低成交价
        # "v": "1000", // 这根K线期间成交量
        # "n": 100, // 这根K线期间成交数量
        # "x": false, // 这根K线是否完结（是否已经开始下一根K线）
        # "q": "1.0000", // 这根K线期间成交额
        # "V": "500", // 主动买入的成交量
        # "Q": "0.500", // 主动买入的成交额
        # "B": "123456" // 忽略此参数
        # }
        # }
        if 'data' in msgobj:
            dataobj = {}
            data = msgobj['data']
            totalvol = float(data['k']['q'])
            totalbvol = float(data['k']['Q'])
            totalsvol = totalvol - totalbvol

            if totalsvol > totalbvol:
                opt = 'sell'
            else:
                opt = 'buy'

            dataobj['time'] = int(data['E'] / 1000)
            dataobj['open'] = float(data['k']['o'])
            dataobj['close'] = float(data['k']['c'])
            dataobj['high'] = float(data['k']['h'])
            dataobj['low'] = float(data['k']['l'])
            dataobj['opt'] = opt
            dataobj['vol'] = totalvol
            dataobj['totalbvol'] = totalbvol
            dataobj['tradecount'] = int(data['k']['n'])
            self.data_handler(dataobj)
        else:
            print('origin data str: ', message)

if __name__ == "__main__":
    # Shipan('dtest2').start()
    sp = DataStream('dtest2')
    sp.start()
