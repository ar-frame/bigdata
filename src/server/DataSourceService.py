# K线数据源
from coop_fetch.Service import Service
import time


class DataSourceService(Service):
    ABC = 0
    TZDATA = {}

    def __init__(self):
        super().__init__()
        # print('start init...')
        DataSourceService.ABC += 1

    def getKDataWorker(self, p1):
        obj = {
            "e": "kline",
            "E": 123456789,
            "s": "BNBBTC",
            "k": {
                "t": 1678359605,
                "T": 1678359605,
                "s": "BNBBTC",
                "i": "1m",
                "f": 100,
                "L": 200,
                "o": "0.0010",
                "c": "0.0020",
                "h": "0.0025",
                "l": "0.0015",
                "v": "1000",
                "n": 100,
                "q": "1.0000",
                "V": "500",
                "Q": "0.500",
                "B": "123456"
            }
        }

        return self.response(obj)


    def mytestWorker(self, p1):
        print('in mytest...' + p1)
        return self.response({'a': p1, "b": 'DataSourceService num %d' % DataSourceService.ABC})
