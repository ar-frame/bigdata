import datetime

from coop_fetch.Service import Service
import time
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

	def pushPBOddDataWorker(self, objodds):
		if objodds and len(objodds) > 0:
			odds = objodds
			matchs = DataService.TZDATA['pb_temp']
			for k in range(len(matchs)):
				match = matchs[k]
				mid = match['id']
				period = match['period']
				# print(mid, period)

				if str(mid) in odds:
					# print('in ....')
					oddmatchs = odds[str(mid)]
					for oddmatch in oddmatchs:
						if period == oddmatch['period']:
							match['ateam']['odds'] = oddmatch['oddA']
							match['bteam']['odds'] = oddmatch['oddB']
							break
			DataService.TZDATA['pb'] =  {"data": matchs, "uptime": int(time.time())}
		return self.response({"msg": "odds push %s succ..." % 'pb'})

	def getPbOddsWorker(self, mark):
		obj = DataService.TZDATA['pbodds']
		return self.response(obj)

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
		# key = tz + '_token'
		DataService.TZDATA[key] = data
		return self.response(res)

	def getDataByKeyWorker(self, key):
		res = {}
		# key = tz + '_token'
		if key in DataService.TZDATA:
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