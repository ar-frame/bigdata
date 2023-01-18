from flask import request
from .ApplicationServiceHttp import ApplicationServiceHttp
from flask import Flask


class EndpointAction(object):

    def __init__(self, action, serverkey):
        self.action = action
        self.serverkey = serverkey
        self.aservice = None

    def __call__(self, *args):
        return self.doallaction()

    def doallaction(self):
        if self.aservice == None:
            self.aservice = ApplicationServiceHttp(self.serverkey)

        if request.method == 'POST':
            # print('post ...')
            if 'ws' in request.form:
                ws = request.form['ws']
                return self.aservice.start(ws)
            else:
                return 'not format'
        else:
            return 'hello coop py server'

class Server(object):
    app = None
    def __init__(self, serverkey, host='localhost', port='5000'):
        self.app = Flask(__name__)
        self.app.logger.disabled = True
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        self.serverkey = serverkey
        self.host = host
        self.port = port

    def run(self):
        # p = Process(target=self.app.run, args=(self.host, self.port,))
        # p.start()
        self.app.run(self.host, self.port, debug=False)

    def add_endpoint(self, endpoint=None, endpoint_name='cooppyserver', handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler, self.serverkey), methods=["GET", "POST"])

# use
# a = Server(serverkey='seraagaldnialaldshgadl12312lasdfaaa', host='localhost', port='5000')
# a.add_endpoint(endpoint='/')
# a.run()
