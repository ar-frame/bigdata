import datetime
from coop_fetch.Service import Service
import time
from binance.spot import Spot as Client
import cfg
import func
from dbconn import MongoDB
class DataService(Service):
	ABC = 0
	TZDATA = {}
	def __init__(self):
		super().__init__()
		# print('start init...')
		DataService.ABC += 1

	def mytestWorker(self, p1):
		print('in mytest...' + p1)
		return self.response({'a': p1, "b": 'num %d' % DataService.ABC})

	def pushDataWorker(self, objstr, tz):
		# print("objstr:", objstr, type(objstr), tz)

		if tz == 'pb':
			DataService.TZDATA[tz+"_temp"] = objstr
		else:
			DataService.TZDATA[tz] = {"data": objstr, "uptime": int(time.time())}
		return self.response({"msg": "push %s succ..." % tz})

	def getDataWorker(self, tz):
		res = {}
		if tz in DataService.TZDATA:
			res = DataService.TZDATA.get(tz)
		return self.response(res)

	def setTokenWorker(self, tz, data):
		res = {}
		key = tz + '_token'
		DataService.TZDATA[key] = data
		return self.response(res)

	def getTokenWorker(self, tz):
		res = {}
		key = tz + '_token'
		if key in DataService.TZDATA:
			res = DataService.TZDATA[key]
		return self.response(res)

	def setDatakeyWorker(self, key, data):
		res = {}
		if key.find('_kline_tickdata') > -1:
			tick_data = data['tick_data']
			del(data['tick_data'])
			infos = data
			if key in DataService.TZDATA:
				origin_data = DataService.TZDATA[key]
				if len(origin_data) < 500:
					origin_data.append(tick_data)
				else:
					origin_data.pop(0)
					origin_data.append(tick_data)
			else:
				origin_data = [tick_data]

			DataService.TZDATA[key] = origin_data
			DataService.TZDATA[key+'_infos'] = infos
		else:
			DataService.TZDATA[key] = data
		return self.response(res)

	def getDataByKeyWorker(self, key):
		res = {}
		if key in DataService.TZDATA:
			if key.find('_kline_tickdata') > -1:
				datas = DataService.TZDATA[key]
				datas_infos = DataService.TZDATA[key+'_infos']
				res = {"data": datas, "infos": datas_infos}
			else:
				res = DataService.TZDATA[key]
		else:
			if key.find('kline_lock') > -1:
				DataService.TZDATA[key] = 'unlock'
				res = DataService.TZDATA[key]

		return self.response(res)

	def checkDataOnlineWorker(self, tz):
		nowtime = int(time.time())
		data = DataService.TZDATA.get(tz)
		if data is not None:
			if nowtime - int(data['uptime']) < 30:
				print('res True')
				return self.response(True)
		return self.response(False)

	def getKlineHisDataWorker(self, symbol, startTime=None, endTime=None, fromStore=True):
		print('getKlineHisDataWorker in')
		symbol = func.formatSymbolName(symbol)
		klinedata = []
		if fromStore:
			klinedata = func.getKlineDataFromStore(symbol, startTime, endTime)
			# print('klinedata s ', klinedata)
			if len(klinedata) > 0:
				print('cache hit')

		if len(klinedata) == 0:
			# print('usec 0')
			startTime = func.transF1DateToTime(startTime)
			endTime = func.transF1DateToTime(endTime)
			limit = 1000
			dataStartTime = startTime
			dataEndTime = endTime
			if endTime is not None and startTime is not None:
				timesep = endTime - startTime + 1
				if timesep > limit:
					if timesep % limit == 0:
						loop = int(timesep / limit)
					else:
						loop = int(timesep / limit) + 1
					for i in range(loop):

						startTime = i * limit + dataStartTime
						endTime = startTime + limit - 1
						if i == loop - 1:
							endTime = dataEndTime

						# print(startTime,'-loop-' ,endTime)
						loopdata = self.getHisData(symbol, startTime * 1000, endTime * 1000)
						klinedata = klinedata + loopdata
				else:
					klinedata = self.getHisData(symbol, startTime * 1000, endTime * 1000)
			else:
				klinedata = self.getHisData(symbol)

		klinedata = func.resortAndRedumplicatedItems(klinedata, 'time')
		return self.response(klinedata)

	def getHisData(self, symbol, startMsTime=None, endMsTime=None):
		# [
		#   [
		#     1499040000000,      // Kline open time
		#     "0.01634790",       // Open price
		#     "0.80000000",       // High price
		#     "0.01575800",       // Low price
		#     "0.01577100",       // Close price
		#     "148976.11427815",  // Volume
		#     1499644799999,      // Kline Close time
		#     "2434.19055334",    // Quote asset volume
		#     308,                // Number of trades
		#     "1756.87402397",    // Taker buy base asset volume
		#     "28.46694368",      // Taker buy quote asset volume
		#     "0"                 // Unused field, ignore.
		#   ]
		# ]
		localproxy = cfg.getCfg().get('set', 'httpproxies')
		proxies = None
		if localproxy is not None:
			proxies = {'https': 'http://' + localproxy}

		# print(proxies)
		spot_client = Client(proxies=proxies)

		# limit (int, optional): limit the results. Default 500; max 1000.
		# startTime (int, optional): Timestamp in ms to get aggregate trades from INCLUSIVE.
		# endTime (int, optional): Timestamp in ms to get aggregate trades until INCLUSIVE.

		limit = 1000
		kline = spot_client.klines(symbol, "1s", limit=limit, startTime=startMsTime, endTime=endMsTime)
		klinedata = []
		for data in kline:
			totalvol = float(data[5]);
			totalbvol = float(data[-3])
			totalsvol = totalvol - totalbvol
			if totalsvol > totalbvol:
				opt = 'sell'
			else:
				opt = 'buy'

			dataobj = {
				"time": int(int(data[0]) / 1000),
				"open": float(data[1]),
				"high": float(data[2]),
				"low": float(data[3]),
				"close": float(data[4]),
				"vol": float(totalvol),
				"opt": opt,
				"totalbvol": float(totalbvol),
				"tradecount": int(data[-4])
			}

			avg = dataobj['high'] - (dataobj['high'] - dataobj['low']) / 2
			dataobj['avg'] = avg
			# dataobj['close'] = avg

			klinedata.append(dataobj)

		return klinedata