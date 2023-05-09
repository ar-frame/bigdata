import json
import multiprocessing
import time
from PyQt6.QtCore import QThread, pyqtSignal
import sys
sys.path.append('../')
import cfg
from Trade import Trade

fetch = cfg.getFetch()
def updateTzStatus():
    checklist = []
    accounts = cfg.getAccountConfig(True)
    for i,account in accounts.iterrows():
        cobj = {}
        account_name = account['用户名']
        cobj['account_name'] = account_name
        cobj['online'] = False
        cobj['balance'] = '-'
        cobj['margin_level'] = '-'
        try:
            td = Trade(account_name)
            if (td.checkIsRealTrading()):
                cobj['online'] = True
                accounts = td.get_accounts()
                cobj['balance'] = '%.2f' % float(accounts['real_total_assetnum'])
                cobj['margin_level'] = '%.2f' % float(accounts['margin_level'])
                cobj['balance'] = cobj['balance'] + '@' + cobj['margin_level']
                # print(accounts)
        except Exception as e:
            # print(e)
            pass
        checklist.append(cobj)
    fetch.getObject('server.Data', 'setDatakey', ['TIME_TZ_STATUS', json.dumps(checklist)])

class WorkerTimerTzStatusThread(QThread):
    trigger = pyqtSignal(str)
    def __int__(self):
        super(WorkerTimerTzStatusThread, self).__init__()

    def stop_server(self):
        print('stop worker tz timer server..')
        try:
            if self.p is not None:
                self.p.terminate()
        except Exception as e:
            pass

    def run(self):
        while True:
            # print('update tz status...')
            try:
                self.p = p = multiprocessing.Process(target=updateTzStatus)
                p.start()
                p.join()
                try:
                    checkliststr = fetch.getString('server.Data', 'getDataByKey', ['TIME_TZ_STATUS'])
                    self.trigger.emit(checkliststr)
                except Exception as e:
                    print('checkliststr:', e)
            except Exception as e:
                print('update tz status timer e:', e)
            time.sleep(10)

if __name__ == "__main__":
    print('--main--')
    updateTzStatus()