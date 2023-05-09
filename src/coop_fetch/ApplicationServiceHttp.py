import traceback

from .Cipher import Cipher
from .Service import Service
import json
import importlib
import sys
import os
import urllib.parse

class ApplicationServiceHttp:
    def __init__(self, serverkey):
        self.serverkey = serverkey

    def start(self, ws):
        self.ws = ws
        try:
            basedir = os.path.dirname(os.path.dirname(__file__))
            sys.path.append(basedir)
            data = self.parseHttpServiceHanlder(self.ws)
            # print('data..', data)
            if data['authSign']['AUTH_SERVER_OPKEY'] != self.serverkey:
                raise(Exception('serverkey error'))

            md = importlib.import_module(data['class'])
            server_class_name = data['class'].split('.')[-1]
            param = json.loads(data['param'])
            # print('orgin data:', data['param'], param)
            class_of_module_obj = getattr(md, server_class_name)
            instance_of_cmo = class_of_module_obj()
            # instance_of_cmo.__init__()
            method_of_cmo = getattr(instance_of_cmo, data['method'])
            ret = method_of_cmo(*param)
            return ret
        except Exception as e:
            traceback.print_exc()
            msg = {"SYSTEM_ERROR": 1, 'errMsg': str(e)}
            return Service().response(msg)

    def parseHttpServiceHanlder(self, ws):
        # print('ws', ws)
        datastr = self.decrypt(ws)
        # print('datastr', datastr)
        datastr = urllib.parse.unquote(datastr)
        # print('datastr2', datastr)
        dataobj = json.loads(datastr)

        if 'data' not in dataobj:
            raise(Exception('data error'))

        classname = dataobj['data']['class'] + 'Service'
        methodname = dataobj['data']['method'] + 'Worker'
        param = dataobj['data']['param']
        auth_sign = dataobj['data']['authSign']
        client_server = dataobj['data']['CLIENT_SERVER']

        return {
            "class": classname,
            "method": methodname,
            "param": param,
            "authSign": auth_sign,
            "CLIENT_SERVER": client_server,
        }

    def decrypt(self, ws):
        return Cipher.hexStr2Str(ws)

    def encrypt(self, ws):
        return Cipher.str2HexStr(ws)

    def runService(self):
        print("run service")