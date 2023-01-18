import datetime
import threading
import time
from PyQt6.QtCore import QThread, pyqtSignal
from multiprocessing import Process
from urllib.parse import urlparse
import asyncio
import sys
from mitmproxy import options,http
from mitmproxy.tools import dump
import json
import cfg
import tools
import DATA_BTC

fetch = cfg.getFetch()
def start_server(startmark = 'START' ):
    if startmark == 'START':
        DATA_BTC.start()
    else:
        print('st:', startmark)

class WorkerDataListenThread(QThread):
    trigger = pyqtSignal(str)

    def __int__(self):
        # 初始化函数
        super(WorkerDataListenThread, self).__init__()

    def stop_server(self):
        print('stop listen server..')
        try:
            if self.p is not None:
                self.p.terminate()
        except Exception as e:
            pass
        print('stop data listen server')

    def run(self):
        self.p = p = Process(target=start_server, args=('START', ))
        p.start()
        p.join()
