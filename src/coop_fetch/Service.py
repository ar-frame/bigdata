import json
from .Cipher import Cipher
class Service:
	TAG_MSG_SEP = '___SERVICE_STD_OUT_SEP___'

	def __init__(self):
		# print('main service in ...')
		pass

	def response(self, obj):
		res = self.TAG_MSG_SEP + self.encrypt(obj)
		return res

	def encrypt(self, obj):
		otype = self.typeof(obj)
		retdata = {
			"type": otype,
			"data": obj
		}
		return Cipher.str2HexStr(json.dumps(retdata))

	def typeof(self, variate):
		type = None
		if isinstance(variate, bool):
			type = "bool"
		elif isinstance(variate, int):
			type = "int"
		elif isinstance(variate, str):
			type = "string"
		elif isinstance(variate, float):
			type = "float"
		elif isinstance(variate, list):
			type = "array"
		elif isinstance(variate, tuple):
			type = "array"
		elif isinstance(variate, dict):
			type = "object"
		elif isinstance(variate, set):
			type = "object"
		else:
			type = 'other'
		return type