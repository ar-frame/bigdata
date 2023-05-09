from coop_fetch.Service import Service
class TestService(Service):
	def mytestWorker(self, p1):
		# print('in mytest...' + p1)
		return self.response({'a': p1, "b": '返回的是繁體的餓哦'})