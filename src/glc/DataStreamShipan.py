#!/usr/bin/env python
import json
import logging
import time
import traceback

from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
# config_logging(logging, logging.DEBUG)
from dbconn import MongoDB
import func
import cfg
fetch = cfg.getFetch()
class DataStreamShipan:
    def __init__(self, account_name):
        key_cfg = cfg.getAccountCfg(account_name, stg=True)
        self.stgconfig = key_cfg
        self.symbol = self.stgconfig.get('set', 'TRADE_VARIETY').lower().replace('-', '').replace('_', '').strip()

    def on_error(self):
        print('on error 111...')

    def on_close(self):
        print('on on_close 111...')

    def start(self):
        print('main start.............')
        logtimemsg = '实盘:' + self.tradeVariety
        self.trade.logOrders(msg=logtimemsg, isclear=True)
        self.trade.orders = self.trade.getRecentOrders()

        while True:
            try:
                tickdata = self.trade.getKline()
                self.data_handler(tickdata)
                time.sleep(1)
            except Exception as e:
                print('main start exception ', e)
                cfg.write_log('stg_shipan_error_main_log', e)
                cfg.write_log('stg_shipan_error_main_log', traceback.print_exc())
                cfg.write_log('stg_shipan_error_main_log', 'traceback.format_exc():\n%s' % traceback.format_exc())
                time.sleep(5)

        print('start end....')

    def stop(self):
        print('stop...')

    def data_handler(self, data):
        print('origin todos data..',  data)

if __name__ == "__main__":
    # Shipan('dtest2').start()
    sp = DataStreamShipan('dtest2')
    sp.start()
