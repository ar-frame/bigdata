import time
import json
import os
import datetime
from decimal import Decimal
import pandas as pd

from dbconn import MongoDB
import cfg
import pytz
from operator import itemgetter

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def transTimeToTimedate(tstime, isUTC=False):
    f2 = '%Y%m%d%H%M%S'
    if isUTC:
        tstime = tstime + 8 * 3600
    t = datetime.datetime.fromtimestamp(tstime, pytz.timezone('Asia/Shanghai')).strftime(f2)
    return t

def transTimeToTimedateF1(tstime, isUTC=False):
    f1 = '%Y-%m-%d %H:%M:%S'
    if isUTC:
        tstime = tstime + 8 * 3600
    t = datetime.datetime.fromtimestamp(tstime, pytz.timezone('Asia/Shanghai')).strftime(f1)
    return t

def transTimedateToTime(timedate):
    if timedate is None:
        timedate = transTimeToTimedate(int(time.time()))
    f2 = '%Y%m%d%H%M%S'
    timedate_stuct = time.strptime(str(timedate), f2)
    tm_s = time.mktime(timedate_stuct)
    return int(tm_s)

def transF1DateToTime(timedate):
    f = '%Y-%m-%d %H:%M:%S'
    timedate_stuct = time.strptime(str(timedate), f)
    tm_s = time.mktime(timedate_stuct)
    return int(tm_s)

def transTimedateToDate(timedate=None):
    ts = transTimedateToTime(timedate)
    return transTimeToTimedateF1(ts)

def transF1ToTimedateF2(dateFormatF1):
    f1 = '%Y-%m-%d %H:%M:%S'
    f2 = '%Y%m%d%H%M%S'

    timedate_stuct = time.strptime(str(dateFormatF1), f1)
    tm_s = time.mktime(timedate_stuct) + 8 * 3600

    tm_s_stu = time.gmtime(tm_s)
    return time.strftime(f2, tm_s_stu)

def printDataFrame(df):
    if len(df) > 0 :
        filter_ids = ['_id', 'id']

        for ids in filter_ids:
            if ids in df:
                del(df[ids])

        dumpstr = ""
        joinConnector = " "
        columns = df.columns.insert(0, 'index')
        padLen = 8
        padlongkeys = ['currency', 'price', 'ptime', 'time']
        padLongLen = 20
        for index,row in df.iterrows():
            if index == 0:
                header = []
                for col in columns:

                    if str(col) in padlongkeys:
                        header.append(str(col).ljust(padLongLen))
                    else:
                        header.append(str(col).ljust(padLen))

                    dumpstr = joinConnector . join(header)

            vals = [str(index).ljust(padLen)]

            for itemkey in dict(row).keys():
                # print('row..', row)
                if str(itemkey) in padlongkeys:
                    vals.append(str(row[itemkey]).ljust(padLongLen))
                else:
                    vals.append(str(row[itemkey]).ljust(padLen))

            # dict(row).values()
            rowstr = joinConnector . join(vals)
            dumpstr = dumpstr + "\n" + rowstr

        return ("\ntrade records \n" + dumpstr)
    else:
        return "empty records"

def writeOrderStore(mark, orders):
    if len(orders) > 0:
        ordersStr = json.dumps(orders, cls=DecimalEncoder)
    else:
        ordersStr = ""
    storeFile = os.path.dirname(os.path.realpath(__file__)) + '/data/store-' + mark + '.json'
    with open(storeFile, 'w', encoding='utf-8') as f:
        f.write(ordersStr)

def getOrderFromStoreFile(mark):
    storeFile = os.path.dirname(os.path.realpath(__file__)) + '/data/store-' + mark + '.json'
    if os.path.exists(storeFile):
        with open(storeFile, 'r', encoding='utf-8') as f:
            orderStr = f.read()
            if len(orderStr) > 0:
                return list(json.loads(orderStr))
            else:
                return []
    else:
        return []

def getOrderFromStore(tradeVariety):
    db_type = cfg.getCfg().get('set', 'SHIPAN_DB_TYPE')
    if db_type == 'mysql':
        pass
        # db_mysql = Mysql(tradeVariety)
        # resdata = db_mysql.getOrders(rowCount=100)
        # return resdata
    else:
        mongo_store = cfg.getMongo('store')
        db_mongo_store = MongoDB(mongo_store.get('DB'), 'orders', mongo_store.get('DB_HOST'), mongo_store.get('DB_USER'), mongo_store.get('DB_PASS'), mongo_store.get('DB_PORT'))
        return list(db_mongo_store.query_all(con = {"complete": {"$eq": '0'}})) + list(db_mongo_store.query_all(con = {"complete": {"$eq": 0}}))

def updateKlineData(tradeVariety, starttime, endtime):
    storedata = getKlineDataFromStore(tradeVariety, starttime, endtime)
    if len(storedata) == 0:
        tradeVariety = formatSymbolName(tradeVariety)

        mark = tradeVariety.lower()
        mongo_store = cfg.getMongo('store')
        db_mongo_store = MongoDB(mongo_store.get('DB'), 'kline_'+mark, mongo_store.get('DB_HOST'), mongo_store.get('DB_USER'),
                                 mongo_store.get('DB_PASS'), mongo_store.get('DB_PORT'))

        print('get data')
        datas = cfg.getFetch().getArray('server.Data', 'getKlineHisData', [tradeVariety, starttime, endtime, False])
        print('get data ok')
        print(len(datas))
        if len(datas) > 0:
            db_mongo_store.insert(datas)
        print('data update ok')
        # for data in datas:
        #     if db_mongo_store.query_row({"time": data['time']}) is None:
        #         db_mongo_store.insert(data)

def getKlineDataFromStore(tradeVariety, starttime, endtime):
    tm2 = transF1DateToTime(endtime)
    tm = transF1DateToTime(starttime)

    tradeVariety = tradeVariety.replace('-', '').replace('_', '')
    mark = tradeVariety.lower()
    mongo_store = cfg.getMongo('store')
    db_mongo_store = MongoDB(mongo_store.get('DB'), 'kline_' + mark, mongo_store.get('DB_HOST'),
                             mongo_store.get('DB_USER'),
                             mongo_store.get('DB_PASS'), mongo_store.get('DB_PORT'))

    con = {"time": {"$gte": tm, "$lte": tm2}}
    datas = list(db_mongo_store.query_all(con))
    datas = sorted(datas, key=itemgetter('time'))

    newdatas = []

    for newdata in datas:
        tempdata = newdata
        del tempdata['_id']
        newdatas.append(tempdata)

    return newdatas

# use binance data fetching
def formatSymbolName(name):
    return str(name).upper().replace('-', '').replace('_', '')

# use mongodb store
def formatStoreName(name):
    return formatSymbolName(name).lower()

def setAccountKlineData(account, runtype, data):
    key = (account + '_kline' + runtype).lower()
    cfg.getFetch().getObject('server.Data', 'setDatakey', [key, data])
    return True

def getAccountKlineData(account, runtype):
    key = (account + '_kline' + runtype).lower()
    try:
        return cfg.getFetch().getObject('server.Data', 'getDataByKey', [key])
    except Exception as e:
        print(e)
        return {}

def setAccountTickData(account, data):
    key = (account + '_kline_tickdata').lower()
    cfg.getFetch().getObject('server.Data', 'setDatakey', [key, data])
    return True

def getAccountTickData(account):
    key = (account + '_kline_tickdata').lower()
    try:
        return cfg.getFetch().getObject('server.Data', 'getDataByKey', [key])
    except Exception as e:
        print(e)
        return {}

def getAccountKlineLock(mark):
    key = 'kline_lock' + mark
    status = cfg.getFetch().getString('server.Data', 'getDataByKey', [key])

    if status == 'lock':
        return False
    elif status == 'unlock':
        cfg.getFetch().getObject('server.Data', 'setDatakey', [key, 'lock'])
        return True
    else:
        return False

def releaseAccountKlineLock(mark):
    key = 'kline_lock' + mark
    try:
        cfg.getFetch().getObject('server.Data', 'setDatakey', [key, 'unlock'])
    except Exception as e:
        print('unlock err...', e)
def resortAndRedumplicatedItems(items, key):
    items = sorted(items, key=lambda e: e[key])
    b = {}
    for item in items:
        b[item[key]] = item
    return list(b.values())

def getMongoStoreObject(mark):
    mongo_store = cfg.getMongo('store')
    db_mongo_object = MongoDB(mongo_store.get('DB'), mark, mongo_store.get('DB_HOST'),
                                       mongo_store.get('DB_USER'),
                                       mongo_store.get('DB_PASS'), mongo_store.get('DB_PORT'))
    return db_mongo_object

def clearData():
    # clear temp order
    datadir = BASE_DIR + '/data'
    listfiles = os.listdir(datadir)
    for filename in listfiles:
        realfile = datadir + '/' + filename
        if os.path.isfile(realfile):
            if filename.find('store-orders_recent') > -1:
                os.remove(realfile)

    # clear log
    datadir = BASE_DIR + '/log'
    listfiles = os.listdir(datadir)
    for filename in listfiles:
        realfile = datadir + '/' + filename
        if os.path.isfile(realfile):
            if filename.find('.log') > -1:
                os.remove(realfile)

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)

if __name__ == "__main__":
    # clearData()
    tk = getAccountTickData('btcTUSD')
    # print(tk)
    print(tk['infos']['stockdetails'], tk['infos']['tradedetails'])
    # account = 'trx'
    # # data = {'tick_data': {'a':5, 'b':9}, 'hh': 3, 'uu':[0,2]}
    # # setAccountTickData(account, data)
    # res = getAccountTickData(account)
    # print(res['data'][-1])
    # releaseAccountKlineLock('btc')
    # res = getAccountKlineLock('btc')
    # print(res)
    # 1682672772
    # 1682672762

    # a = [{"tm": 12, "v":1}, {"tm": 22, "v": 3}, {"tm": 22, "v": 34}, {"tm": 10, "v": 55}, {"tm": 44, "v": 66}]
    # b = resortAndRedumplicatedItems(a, 'tm')
    # print(b)
    # print("get str")
    # writeOrderStore()
    # orders = getOrderFromStore('ETH-USDT')
    # print(orders)

    # starttime = '2023-04-15 07:51:00'
    # endtime = '2023-04-15 09:50:00'
    # updateKlineData('BTCUSDT', starttime, endtime)

    # kdata = getKlineDataFromStore('BTCUSDT', starttime, endtime)
    # print(kdata, len(kdata))

