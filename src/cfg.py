import configparser
import os
import logging
import datetime
import json
import pandas as pd
from itertools import combinations, permutations

import func
from dbconn import MongoDB
from coop_fetch.Config import Config
from coop_fetch.Fetch import Fetch

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = BASE_PATH + '/log'
TZ_CONFIG_FILE = os.path.join(BASE_PATH, "conf/tz.csv")
ACCOUNT_CONFIG_FILE = os.path.join(BASE_PATH, "conf/account.csv")
BASE_CONFIG_FILE = os.path.join(BASE_PATH, "conf/conf.ini")
COOKIE_PATH = BASE_PATH + '/cookies'
STGS_PATH = BASE_PATH + '/stgs'

def getCfg(name = None, raw=False):
    if name is None:
        save_file = BASE_CONFIG_FILE
    else:
        if name.find('account.') > -1:
            account_name = name.split('.')[1]
            save_file = os.path.join(getBaseDir(), "trade_accounts/%s/key.ini" % account_name)
            # print(save_file)
        else:
            save_file = os.path.join(getBaseDir(), "conf/%s.ini" % name)

    if raw == True:
        with open(save_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        config = configparser.ConfigParser()
        config.read(save_file, encoding = 'utf-8')
        return config

def save_config(keystr, content, name = None):
    if name is None:
        save_file = BASE_CONFIG_FILE
    else:
        if name.find('account.') > -1:
            account_name = name.split('.')[1]
            save_file = os.path.join(getBaseDir(), "trade_accounts/%s/key.ini" % account_name)
        else:
            save_file = os.path.join(getBaseDir(), "conf/%s.ini" % name)

    config = getCfg(name)

    option = 'DEFAULT'
    key = keystr
    if keystr.find('.') > -1:
        option,key = keystr.split('.')
    config[option][key] = str(content)
    with open(save_file, 'w', encoding='utf-8') as fp:
        config.write(fp)

def getAccountCfg(account, stg=False, raw=False):
    curpath = os.path.dirname(os.path.realpath(__file__))
    fname = 'key'
    if stg == True:
        fname = 'stg'

    cfgpath = os.path.join(curpath, f"trade_accounts/{account}/{fname}.ini")
    if os.path.exists(cfgpath):

        if raw == True:
            with open(cfgpath, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            config = configparser.ConfigParser()
            config.read(cfgpath, encoding='utf-8')
            return config
    else:
        if raw == True:
            if stg == True:
                return getAccountStgInitCfg(account, raw=True)
            else:
                return getCfg(name='account_key_tpl', raw=True)
        else:
            print('account cfg "%s" not found' % cfgpath)
            return None

def saveAccountCfg(account, content, stg=False):
    curpath = os.path.dirname(os.path.realpath(__file__))
    fname = 'key'
    if stg == True:
        fname = 'stg'

    cfgpath = os.path.join(curpath, f"trade_accounts/{account}/{fname}.ini")
    account_path = os.path.dirname(cfgpath)
    if os.path.exists(account_path) == False:
        os.mkdir(account_path)

    with open(cfgpath, 'w+', encoding='utf-8') as f:
        f.write(content)

def getAccountStgInfo(account):
    account_config = getAccountCfg(account)
    stg_name = account_config.get('set', 'STG')
    curpath = os.path.dirname(os.path.realpath(__file__))
    start_script = os.path.join(curpath, f"stgs/{stg_name}/main.py")
    return {"start_script": start_script, "package": "stgs." + stg_name + ".main"}

def getAccountStgInitCfg(account = None, raw=False, stg_name=None):
    if account is not None:
        account_config = getAccountCfg(account)
        stg_name = account_config.get('set', 'STG')
    curpath = os.path.dirname(os.path.realpath(__file__))
    cfgpath = os.path.join(curpath, f"stgs/{stg_name}/main.ini")
    if raw == True:
        with open(cfgpath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        config = configparser.ConfigParser()
        config.read(cfgpath, encoding='utf-8')
        return config

def getMongo(tradeVariety = None):
    cfg = getCfg()
    if tradeVariety is None:
        mongo = cfg.get('set', 'mongo')
    else:
        if tradeVariety == 'ETH-USDT':
            mongo = 'default'
        elif tradeVariety == "EOS-USDT":
            mongo = 'eos'
        elif tradeVariety == "BTC-USDT":
            mongo = 'btc'
        else:
            mongo = tradeVariety.lower()

    # cpair = tradeVariety[0:-5]

    DB = cfg.get('mongo_' + mongo, 'DB')
    DB_PASS = cfg.get('mongo_' + mongo, 'DB_PASS')
    DB_HOST = cfg.get('mongo_' + mongo, 'DB_HOST')
    DB_USER = cfg.get('mongo_' + mongo, 'DB_USER')

    # DB = 'bigdata-' + cpair.lower()
    # DB_PASS = ''
    # DB_HOST = '127.0.0.1'
    # DB_USER = ''

    return {"DB": DB, "DB_PASS": DB_PASS, "DB_USER": DB_USER, "DB_HOST": DB_HOST}

def getMysql():
    cfg = getCfg()
    DB = cfg.get("mysql", 'DB')
    DB_PASS = cfg.get('mysql', 'DB_PASS')
    DB_HOST = cfg.get('mysql', 'DB_HOST')
    DB_USER = cfg.get('mysql', 'DB_USER')
    DB_PORT = int(cfg.get('mysql', 'DB_PORT'))
    print(DB_PORT)
    return {"DB": DB, "DB_PASS": DB_PASS, "DB_USER": DB_USER, "DB_HOST": DB_HOST, "DB_PORT":DB_PORT}

def getGlobalErrorLogFile():
    return os.path.join(getBaseDir(), "log/error.log")

def error_log(msg):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=getGlobalErrorLogFile(), level=logging.DEBUG, format=LOG_FORMAT)
    return logging.debug(str(msg))

def write_log(mark, content):
    if os.path.exists(LOG_PATH) == False:
        os.mkdir(LOG_PATH)
    filename = LOG_PATH + '/' + mark + '.log'
    with open(filename, 'a') as f:
        nowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write("time:%s,msg:%s" % (nowTime, str(content)) + "\n")

def getFetch():
    localserver = getCfg().get('set', 'localserver')
    localserverkey = getCfg().get('set', 'localserverkey')
    server = 'http://' + localserver
    fetch_config = Config(server, localserverkey)
    fetch = Fetch(fetch_config)
    return fetch

def getBaseDir():
    return os.path.dirname(os.path.realpath(__file__))

def getGlobalErrorLogFile():
    return os.path.join(getBaseDir(), "log/error.log")

def error_log(msg):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=getGlobalErrorLogFile(), level=logging.DEBUG, format=LOG_FORMAT)
    return logging.debug(str(msg))

def checkTzEnable(tzmark):
    cfgtz = getTzConfig(DATAFRAME=True)
    pb = cfgtz.loc[cfgtz['MK'] == tzmark.upper()]
    if len(pb) > 0:
        if int(pb.iloc[0]['启用']) == 1:
            return True
        else:
            return False
    else:
        return False

def getMarkVal(tzmark, keyname):
    cfgtz = getTzConfig(DATAFRAME=True)
    pb = cfgtz.loc[cfgtz['MK'] == tzmark.upper()]
    if len(pb) > 0:
        data = pb.iloc[0]
        if keyname in data:
            return data[keyname]
        else:
            return None
    else:
        return None

def getTzConfig(DATAFRAME = False):
    cfgpath = TZ_CONFIG_FILE
    if DATAFRAME == True:
        return pd.read_csv(cfgpath, encoding = 'utf-8', index_col = False)
    tz_obj = {"title": [], "tzs": []}
    try:
        with open(cfgpath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            c_list = content.split("\n")
            tz_obj["title"] = c_list[0].split(',')
            for i in range(len(c_list)):
                if i == 0:
                    continue
                c_row = c_list[i].split(',')
                tz_obj["tzs"].append(c_row)
    except Exception as e:
        print(e)
        error_log(e)
    return tz_obj

def getTzTitles():
    tzs = getTzConfig()
    titles = []
    for tz in tzs['tzs']:
        titles.append(tz[1])
    return titles

def checkAccountNameEnable(account_name):
    df_accounts = getAccountConfig(DATAFRAME=True)
    match_account = df_accounts.loc[df_accounts['用户名'] == account_name]
    return len(match_account) == 0
    # print(len(match_account))

def getAccountConfig(DATAFRAME=False):
    cfgpath = ACCOUNT_CONFIG_FILE
    if DATAFRAME == True:
        return pd.read_csv(cfgpath, encoding = 'utf-8', index_col = False)
    tz_obj = {"title": [], "accounts": []}
    try:
        tz = getTzConfig(True)
        with open(cfgpath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            c_list = content.split("\n")
            tz_obj["title"] = c_list[0].split(',')
            tz_obj["title"][0] = '平台'
            for i in range(len(c_list)):
                if i == 0:
                    continue
                c_row = c_list[i].split(',')
                tzname = tz.loc[tz.ID == int(c_row[0])]['网站'].reset_index(drop=True).loc[0]
                c_row[0] = tzname
                tz_obj["accounts"].append(c_row)
    except Exception as e:
        print(e)
        error_log(e)
    return tz_obj

def getAccount(uid):
    alluser = getAccountConfig(False)
    # print(alluser)
    row = alluser['accounts'][uid]
    user = {}
    for k in range(len(alluser['title'])):
        user[alluser['title'][k]] = row[k]
    return user

def getTzPairs():
    tzs = getTzConfig(DATAFRAME=False)
    tz_list = tzs['tzs']
    c_list = list(combinations(tz_list, 2))
    tz_pairs = []
    for i in range(len(c_list)):
        c_pair = c_list[i]
        obj = {'title': c_pair[0][1] + 'vs' + c_pair[1][1], 'val': c_pair[0][0] + '_' + c_pair[1][0]}
        tz_pairs.append(obj)
    return tz_pairs

def saveTzConfig(df):
    cfgpath = TZ_CONFIG_FILE
    df.set_index('ID', inplace = True)
    return df.to_csv(cfgpath, encoding = 'utf-8')

def saveAccountsConfig(df):
    cfgpath = ACCOUNT_CONFIG_FILE
    df.set_index('TZID', inplace=True)
    return df.to_csv(cfgpath, encoding='utf-8')




def delAccount(rownumber):
    ac = getAccountConfig(True)
    ac = ac.drop(index=rownumber)
    saveAccountsConfig(ac)


def genCookieFile(uid):
    accs = getAccountConfig(DATAFRAME=True)
    selacc = accs.iloc[uid]

    url = selacc['网址']
    username = selacc['用户名']

    url = url.replace('https://', '')
    url = url.replace('http://', '')
    url = url.strip('/')
    cooikeFile = COOKIE_PATH + '/' + url + '_' + username + '.txt'
    return cooikeFile

def getCachePath(uid):
    accs = getAccountConfig(DATAFRAME=True)
    selacc = accs.iloc[uid]

    url = selacc['网址']
    username = selacc['用户名']

    url = url.replace('https://', '')
    url = url.replace('http://', '')
    url = url.strip('/')
    if url.find('/') > -1:
        url = url.split('/')[0]

    cachePath = COOKIE_PATH + '/' + url + '_' + username

    if os.path.exists(COOKIE_PATH) == False:
        os.mkdir(COOKIE_PATH)

    if os.path.exists(cachePath) == False:
        os.mkdir(cachePath)

    return cachePath

def saveBroswerCookie(uid, dictCookies):
    jsonCookies = json.dumps(dictCookies)

    print("cks..", jsonCookies)

    if os.path.exists(COOKIE_PATH) == False:
        os.mkdir(COOKIE_PATH)

    cooikeFile = genCookieFile(uid)

    # print("cks..", jsonCookies, cooikeFile)
    with open(cooikeFile, 'w', encoding='utf-8') as f:
        f.write(jsonCookies)


def getBroserCookie(uid):
    cooikeFile = genCookieFile(uid)
    try:
        with open(cooikeFile, 'r', encoding='utf-8') as f:
            dictCookies = json.loads(f.read())
        return dictCookies
    except Exception as e:
        return {}

def savePointLog(dictinfo):
    now = datetime.datetime.now()
    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
    dictinfo['time'] = nowtime
    jsonStr = json.dumps(dictinfo, ensure_ascii=False)
    print("dictinfo..", dictinfo)
    if os.path.exists(LOG_PATH) == False:
        os.mkdir(LOG_PATH)
    if float(dictinfo['optpoint']['point']) > 2:
        logFile = LOG_PATH + '/point_check.log'
    else:
        logFile = LOG_PATH + '/point.log'

    with open(logFile, 'a+', encoding='utf-8') as f:
        f.write(jsonStr + "\n")

def saveOrderLog(dictinfo):
    now = datetime.datetime.now()
    nowtime = now.strftime("%Y-%m-%d %H:%M:%S")
    dictinfo['time'] = nowtime
    jsonStr = json.dumps(dictinfo, ensure_ascii=False)
    print("dictinfo..", dictinfo)
    if os.path.exists(LOG_PATH) == False:
        os.mkdir(LOG_PATH)

    logFile = LOG_PATH + '/order.log'

    with open(logFile, 'a+', encoding='utf-8') as f:
        f.write(jsonStr + "\n")

def getTzSprofitConfig(tzmark):
    tzconfig = {"enable": False, "profit": 0}
    enable = getCfg().get('sprofit', 'enable')

    tzmarkid = getMarkVal(tzmark.upper(), 'ID')
    pbid = getMarkVal('PB', 'ID')

    enable_key = 'enable%s_%s' % (pbid, tzmarkid)
    profit_key = 'profit%s_%s' % (pbid, tzmarkid)

    enabletz = getCfg().get('sprofit', enable_key)
    profittz = getCfg().get('sprofit', profit_key)

    if int(enable) == 1 and int(enabletz) == 1:
        tzconfig['enable'] = True

    tzconfig['profit'] = float(profittz)

    return tzconfig

def setpid(pid):
    if pid is not None:
        pid = str(pid)

    if os.path.exists(LOG_PATH) == False:
        os.mkdir(LOG_PATH)

    logFile = LOG_PATH + '/pid.txt'

    if pid is None:
        if os.path.exists(logFile):
            os.remove(logFile)
    else:
        with open(logFile, 'w+', encoding='utf-8') as f:
            f.write(pid)

def getpid():
    if os.path.exists(LOG_PATH) == False:
        os.mkdir(LOG_PATH)

    logFile = LOG_PATH + '/pid.txt'
    pid = None
    if os.path.exists(logFile):
        with open(logFile, 'r', encoding='utf-8') as f:
            pid = f.read()
    return pid

def initAccountData(account_name):
    df_accounts = getAccountConfig(DATAFRAME=True)
    match_account = df_accounts.loc[df_accounts['用户名'] == account_name]
    if len(match_account) > 0:
        stg = match_account.iloc[0]['策略']
        stg_content = getAccountStgInitCfg(stg_name=stg, raw=True)
        saveAccountCfg(account=account_name, content=stg_content, stg=True)

        key_content = getCfg(name='account_key_tpl', raw=True)
        saveAccountCfg(account=account_name, content=key_content, stg=False)
        save_config('set.STG', stg, name='account.' + account_name)

def getAccountLatestOrders(account_name):
    acccfg = getAccountCfg(account_name, stg=True)
    variety = acccfg.get('set', 'TRADE_VARIETY')
    mongo_store = getMongo('store')
    db_mongo_store = MongoDB(mongo_store.get('DB'), \
                                  'orders_' + func.formatStoreName(variety) + '_' + account_name,\
                                  mongo_store.get('DB_HOST'), mongo_store.get('DB_USER'), mongo_store.get('DB_PASS'))
    orders = list(db_mongo_store.query_all(con={"complete": {"$eq": 0}}))
    return orders
def getStgLists():
    stgs = []
    file_names = os.listdir(STGS_PATH)
    for fname in file_names:
        abspath = STGS_PATH + '/' + fname
        if os.path.isdir(abspath):
            fini = abspath + '/main.ini'
            if os.path.isfile(fini):
                stgs.append(fname)
    return stgs

if __name__ == "__main__":
    # mongo = getMongo()
    # print(mongo)
    orders = getStgLists()
    print(orders)
    pass

    # isrun = checkAccountProcessIsRun('REALTEST')
    # print(isrun)

    # print(basec.get('app', 'title'),  c.get('set', 'a'))
    # save_config('set.STG', 'NJ',  name='account.dtest')
