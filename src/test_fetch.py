from coop_fetch.ServerResponseException import ServerResponseException
from coop_fetch.Config import Config
from coop_fetch.Fetch import Fetch
from coop_fetch.Cipher import Cipher


config = Config("http://localhost:5000", "aaabbbccccoopserverkey123in")
fetch = Fetch(config)

try:
    tr = fetch.getArray('server.Data', 'getKlineHisData', ['BTCUSDT', '2023-04-06 18:51:00', '2023-04-06 21:39:00'])
    print(type(tr), tr)

except Exception as e:
    print(e)
