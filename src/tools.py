import os
import re
import time

import psutil as psutil

import cfg
import datetime
from datetime import timedelta
import sys

fetch = cfg.getFetch()
def kill_port_process(port):
    # 根据端口号杀死进程
    ret = os.popen("netstat -nao|findstr " + str(port))
    str_list = ret.read()

    if not str_list:
        print('端口未使用')
        return
    # 只关闭处于LISTENING的端口
    if 'TCP' in str_list:
        ret_list = str_list.replace(' ', '')
        ret_list = re.split('\n', ret_list)
        listening_list = [rl.split('LISTENING') for rl in ret_list]
        process_pids = [ll[1] for ll in listening_list if len(ll) >= 2]
        process_pid_set = set(process_pids)
        for process_pid in process_pid_set:
            os.popen('taskkill /pid ' + str(process_pid) + ' /F')
            print(port, '端口已被释放')
            time.sleep(1)

    elif 'UDP' in str_list:
        ret_list = re.split(' ', str_list)
        process_pid = ret_list[-1].strip()
        if process_pid:
            os.popen('taskkill /pid ' + str(process_pid) + ' /F')
            print('端口已被释放')
        else:
            print("端口未被使用")

def kill_pid(pid):
    os.popen('taskkill /pid ' + str(pid) + ' /F')

def check_pid(pid):
    try:
        psutil.Process(pid)
    except Exception as e:
        return False
    else:
        return True

def process_exists(pid, remoteSystem=None):
    if remoteSystem is None:
        remoteSystem = RemoteSystem()

    # Check if process is still running for Windows:
    try:
        if "ProcessId" in remoteSystem.execute(["wmic", "PROCESS", "where", "ProcessId=%s" % pid, "GET", "ProcessId"])[1]:
            return True
    except:
        pass

    # Check if process is still running for Unix:
    try:
        if remoteSystem.execute(["ps", "--pid", "%s" % pid])[0] == "0":
            return True
    except:
        pass
    return False

def get_payback_point(p0, p1):
    p0 = float(p0)
    p1 = float(p1)
    p = 100 / (100 / p0 + 100 / p1)
    return float("%.5f" % p)

def get_p4(p0, p1, p2, p3):
    opt = None
    point_f = get_payback_point(p0, p3)
    point_s = get_payback_point(p1, p2)
    point = 0
    if point_f > point_s:
        point = point_f
        opt = {"optp0": 0, "optp1": 3, "odds0": p0, 'odds1': p3}
    else:
        point = point_s
        opt = {"optp0": 1, "optp1": 2, "odds0": p1, 'odds1': p2}

    if point > 1:
        opt['point'] = point
        opt['canopt'] = 1
    else:
        opt['point'] = point
        opt['canopt'] = 0

    opt['point'] = float("%.5f" % float(opt['point']))
    return opt

def get_monday_to_sunday(today, weekly=0):
    """
    :function: 获取指定日期的周一和周日的日期
    :param today: '2021-11-16'; 当前日期：today = datetime.now().strftime('%Y-%m-%d')
    :param weekly: 获取指定日期的上几周或者下几周，weekly=0当前周，weekly=-1上一周，weekly=1下一周
    :return: 返回指定日期的周一和周日日期
    :return_type: tuple
    """
    last = weekly * 7
    today = datetime.datetime.strptime(str(today), "%Y-%m-%d")
    monday = datetime.datetime.strftime(today - timedelta(today.weekday() - last), "%Y-%m-%d")
    monday_ = datetime.datetime.strptime(monday, "%Y-%m-%d")
    sunday = datetime.datetime.strftime(monday_ + timedelta(monday_.weekday() + 6), "%Y-%m-%d")
    return [monday, sunday]

def get_all_match(aname, bname):
    matchs = fetch.getObject('server.Data', 'getData', ['pb'])
    findmatchs = []
    for i in range(len(matchs['data'])):
        crow = matchs['data'][i]
        ateam = crow['ateam']
        bteam = crow['bteam']
        if ateam['name'] == aname:
            if bteam['name'] == bname:
                findmatchs.append(crow)
    return findmatchs

def get_pbpoint_bynamepair(aname, bname, reverse = False):
    matchs = fetch.getObject('server.Data', 'getData', ['pb'])
    # print("pb matchs:", type(matchs),matchs, len(matchs['data']))
    pbdatas = matchs['data']
    matchpoint = {}
    findobji = None
    for i in range(len(matchs['data'])):
        crow = matchs['data'][i]
        ateam = crow['ateam']
        bteam = crow['bteam']

        if crow['period'] == 0:

            if ateam['name'] == aname:
                if bteam['name'] == bname:

                    findobji = i
                    break
                elif len(bteam['name']) > len(bname):
                    if bteam['name'].find(bname) > -1:
                        findobji = i
                        break
                else:
                    if bname.find(bteam['name']) > -1:
                        findobji = i
                        break
            elif len(ateam['name']) > len(aname):
                if ateam['name'].find(aname) > -1:
                    if bteam['name'] == bname:
                        findobji = i
                        break
                    elif len(bteam['name']) > len(bname):
                        if bteam['name'].find(bname) > -1:
                            findobji = i
                            break
                    else:
                        if bname.find(bteam['name']) > -1:
                            findobji = i
                            break
            else:
                if aname.find(ateam['name']) > -1:
                    if bteam['name'] == bname:
                        findobji = i
                        break
                    elif len(bteam['name']) > len(bname):
                        if bteam['name'].find(bname) > -1:
                            findobji = i
                            break
                    else:
                        if bname.find(bteam['name']) > -1:
                            findobji = i
                            break

    if findobji is None:
        print('not found match')
        if reverse == False:
            reverse = True
            return get_pbpoint_bynamepair(bname, aname, reverse)
        else:
            return None
    else:
        match = matchs['data'][findobji]
        if reverse == True:
            ateam = match['ateam']
            bteam = match['bteam']
            match['ateam'] = bteam
            match['bteam'] = ateam

        match['ateam']['odds'] = "%.2f" % float(match['ateam']['odds'])
        match['bteam']['odds'] = "%.2f" % float(match['bteam']['odds'])
        return match

def getFirstNearInt10(val):
    val = int(val)

    while True:
        # print(val)
        if val < 10:
            val = val + 1
            continue
        if val % 10 == 0:
            return val
        else:
            val = val + 1
            continue

# 独立利润
def getBuyAmountSingle(amount, profit, optpoint):
    buyamount = 0
    if optpoint['canopt'] == 1:
        if amount > 0 and optpoint['point'] > 1:
            if amount * (optpoint['point'] - 1) >= profit:
                buyamount = getFirstNearInt10(amount / optpoint['odds1'])

    return buyamount

# 单式注额
def getBuyAmountDanshi(mark, odds):
    buyamount = 0
    amount = cfg.getMarkVal(mark.upper(), '单式注额')
    amount = float(amount)
    if amount > 0:
        buyamount = getFirstNearInt10(amount / odds)
    return buyamount

def checkMainProcessStatusAndExit():
    try:
        pid = cfg.getpid()
        if pid is None:
            print('main status exit')
            sys.exit()
    except Exception as e:
        print('checkMainProcessStatusAndExit e:', e)

def setAccountProcess(account_name, pid):
    setkey = 'process_' + account_name
    pushobj = fetch.getObject('server.Data', 'setDatakey', [setkey, pid])

def getAccountProcessId(account_name):
    setkey = 'process_' + account_name
    try:
        pid = fetch.getInt('server.Data', 'getDataByKey', [setkey])
        return pid
    except Exception as e:
        return None

def checkAccountProcessIsRun(account_name):
    pid = getAccountProcessId(account_name)
    if pid is not None:
        return check_pid(pid)
    else:
        return False

if __name__ == '__main__':
    # f = getFirstNearInt10(31.33)
    # print('f:', f)

    isrun = checkAccountProcessIsRun('REALTEST')

    print(isrun)
    # kill_pid(7704)
    pass