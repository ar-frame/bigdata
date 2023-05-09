import os
import time
from PyQt6.QtCore import QThread, pyqtSignal
import sys
import http.server
import socketserver

sys.path.append('../')
from coop_fetch.Server import Server

from multiprocessing import Process
import tools
import cfg

DIRECTORY = 'chart/build'
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def translate_path(self, path):
        print('inpath', path)
        path = http.server.SimpleHTTPRequestHandler.translate_path(self, path)
        print('newpath', path)
        if os.path.isdir(path) == False:
            if path.find('.') == -1:
                path = DIRECTORY
        return path

def start_server(startmark = 'START' ):
    if startmark == 'START':
        servercfg = cfg.getCfg().get('set', 'localwebserver')
        host = servercfg.split(':')[0]
        port = int(servercfg.split(':')[1])
        tools.kill_port_process(port)

        with socketserver.TCPServer(("", port), Handler) as httpd:
            print("web serving at port", port)
            httpd.serve_forever()
    else:
        print('st:', startmark)

class WorkerWebServerThread(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    trigger = pyqtSignal(str)

    def __int__(self):
        # 初始化函数
        super(WorkerWebServerThread, self).__init__()

    def stop_server(self):
        print('stop worker web server..')
        try:
            if self.p is not None:
                self.p.terminate()
        except Exception as e:
            pass

    def run(self):
        self.p = p = Process(target=start_server, args=('START', ))
        p.start()

if __name__ == "__main__":
    start_server('START')