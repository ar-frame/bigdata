import time
from PyQt6.QtCore import QThread, pyqtSignal
import sys
sys.path.append('../')
from coop_fetch.Server import Server

from multiprocessing import Process
import tools
import cfg

def start_server(startmark = 'START' ):
    if startmark == 'START':
        servercfg = cfg.getCfg().get('set', 'localserver')
        host = servercfg.split(':')[0]
        port = int(servercfg.split(':')[1])
        tools.kill_port_process(port)

        serverkey = cfg.getCfg().get('set', 'localserverkey')
        a = Server(serverkey=serverkey, host=host, port=port)
        a.add_endpoint(endpoint='/')
        a.run()
    else:
        print('st:', startmark)

class WorkerThread(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    trigger = pyqtSignal(str)

    def __int__(self):
        # 初始化函数
        super(WorkerThread, self).__init__()

    def stop_server(self):
        print('stop worker server..')
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