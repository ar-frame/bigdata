import importlib
import json
import os
import sys
import time
import traceback

from PyQt6.QtCore import QThread, pyqtSignal

from coop_fetch.Server import Server

from multiprocessing import Process

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service

import time
from lxml import etree
import cfg
from subprocess import CREATE_NO_WINDOW

import tools
fetch = cfg.getFetch()
def start_server(startmark = 'START', uid = 0):
    if startmark == 'START':
        print('load uid:', uid)
        selacc = cfg.getAccount(uid)
        username = selacc['用户名']
        print('selaccount:', username)
        processname = username
        if tools.checkAccountProcessIsRun(username, shipan=True) == True:
            print('process is running...', username)
        else:
            tools.setAccountProcess(processname, os.getpid(), shipan=True)
            try:
                stgobj = cfg.getAccountStgInfo(username)
                basedir = os.path.dirname(stgobj['start_script_shipan'])
                sys.path.append(basedir)
                md = importlib.import_module(stgobj['package_shipan'])
                server_class_name = 'Shipan'
                param = [username]
                class_of_module_obj = getattr(md, server_class_name)
                instance_of_cmo = class_of_module_obj(account_name=username)
                method_of_cmo = getattr(instance_of_cmo, 'start')
                ret = method_of_cmo()
                return ret
            except Exception as e:
                print('stg shipan run error:', e)
                cfg.write_log('stg_shipan_error_log', e)
                cfg.write_log('stg_shipan_error_log', json.dumps([username, stgobj]))
                cfg.write_log('stg_shipan_error_log', traceback.print_exc())
                cfg.write_log('stg_shipan_error_log', 'traceback.format_exc():\n%s' % traceback.format_exc())
                tools.setAccountProcess(processname, None, shipan=True)
    else:
        print('st:', startmark)

class WorkerStgShipanThread(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    trigger = pyqtSignal(str)

    def __int__(self, *__args):
        # 初始化函数
        super(WorkerStgShipanThread, self).__init__()
        self.url = ''

    def stop_server(self):
        print('stop stg shipan server..')
        try:
            if self.p is not None:
                self.p.terminate()
        except Exception as e:
            pass

    def set_login_uid(self, uid):
        self.uid = uid

    def run(self):
        print('p run:', os.getpid())
        self.p = p = Process(target=start_server, args=('START', self.uid, ))
        p.start()


