import json
import multiprocessing
import time
from PyQt6.QtCore import QThread, pyqtSignal
import cfg
import tools
fetch = cfg.getFetch()
def updateAccountStatus():
    account_config = cfg.getAccountConfig()
    accounts = account_config['accounts']
    title = account_config['title']
    for i in range(len(accounts)):
        account_name = accounts[i][title.index('用户名')]
        # print(account_name)
        isonline = tools.checkAccountProcessIsRun(account_name)
        online_text = ''
        if isonline:
            online_text = '运行中...'
        colindex = title.index('状态')
        df = cfg.getAccountConfig(DATAFRAME=True)
        df.iloc[i, colindex] = online_text
        cfg.saveAccountsConfig(df)

class WorkerTimerAccountProcessStatusThread(QThread):
    trigger = pyqtSignal(str)

    def __int__(self):
        super(WorkerTimerAccountProcessStatusThread, self).__init__()

    def stop_server(self):
        print('stop worker timer server..')
        try:
            if self.p is not None:
                self.p.terminate()
        except Exception as e:
            pass

    def run(self):
        while True:
            print('update account status...')
            try:
                self.p = p = multiprocessing.Process(target=updateAccountStatus)
                p.start()
                p.join()
            except Exception as e:
                print('update account status timer e:'. e)

            self.trigger.emit('update')
            time.sleep(5)


