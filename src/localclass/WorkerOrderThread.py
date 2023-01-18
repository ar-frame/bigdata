import json
import multiprocessing
import time
from PyQt6.QtCore import QThread, pyqtSignal

import cfg

from Trade import Trade

fetch = cfg.getFetch()


def updateJobData(mark):
    try:
        jsonstr = Trade(mark).getTradeResult()
    except Exception as e:
        jsonstr = {}

    if jsonstr is None:
        jsonstr = {}
    jsonstr['mark'] = mark
    jsonstr = json.dumps(jsonstr)
    fetch.getObject('server.Data', 'setDatakey', ['ORDER_LIST_STR', jsonstr])

class WorkerOrderThread(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    trigger = pyqtSignal(str)

    def __int__(self):
        # 初始化函数
        super(WorkerOrderThread, self).__init__()
        self.mark = ''

    def set_current_mark(self, mark):
        self.mark = mark

    def stop_server(self):
        print('stop order server..')
        try:
            if self.p is not None:
                self.p.terminate()
        except Exception as e:
            pass

    def run(self):
        print('start order run...')
        if self.mark == '':
            print('mark load empty')
        else:
            try:
                self.p = p = multiprocessing.Process(target=updateJobData, args=(self.mark, ))
                p.start()
                p.join()

                try:
                    jsonStr = fetch.getString('server.Data', 'getDataByKey', ['ORDER_LIST_STR'])
                    self.trigger.emit(jsonStr)
                except Exception as e:
                    print('orderliststr:', e)

            except Exception as e:
                print('work order e: ', e)

        #
        # for i in range(20):
        #     time.sleep(1)
        #     self.trigger.emit(str(i))


