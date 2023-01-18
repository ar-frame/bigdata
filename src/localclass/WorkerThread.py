import time
from PyQt6.QtCore import QThread, pyqtSignal

from coop_fetch.Server import Server

from multiprocessing import Process
import tools

def start_server(startmark = 'START' ):
    if startmark == 'START':

        port = 5000
        tools.kill_port_process(port)

        a = Server(serverkey='aaabbbccccoopserverkey123in', host='localhost', port='5000')
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
        #重写线程执行的run函数
        #触发自定义信号

        # print('run ...')
        # return

        # a = Server(serverkey='aaabbbccccoopserverkey123in', host='localhost', port='5000')
        # a.add_endpoint(endpoint='/')
        # a.run()

        self.p = p = Process(target=start_server, args=('START', ))
        p.start()

        # a = Server(serverkey='aaabbbccccoopserverkey123in', host='localhost', port='5000')
        # a.add_endpoint(endpoint='/')
        # a.run()

        # for i in range(20):
        #     time.sleep(1)
        #     self.trigger.emit(str(i))


