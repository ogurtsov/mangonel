import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line

import sockjs.tornado

import os
import json


define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class RequestBodyParser():
    data = {}
    def __init__(self, request):
        self.data = json.loads(request.body)
    def get(self, field, default=None):
        return self.data.get(field, default)

class DemoHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class PubSub(sockjs.tornado.SockJSConnection):
    participants = set()
    channel = None
    default_channel = 'default'
    channels = {}

    def on_open(self, request):
        # Send that someone joined
        #self.broadcast(self.participants, "Someone joined.")        

        # Add client to the clients list
        #self.participants.add(self)
        pass

    def on_message(self, message):
        try:
            data = json.loads(message)
        except:
            data = {}

        # method router (todo: switch to switch)
        method = data.get('method', 'no-method')
        if method == 'broadcast':
            self._broadcast(data.get('data', {}))
        elif method == 'set-channel':
            self.set_channel(data.get('data', {}))
        else:
            self.placeholder(data.get('data', {}))

    def _broadcast(self, data):
        self.broadcast(self.channels[self.channel], json.dumps(data))

    def placeholder(self, data):
        pass

    def set_channel(self, data):
        self.channel = data.get('channel', self.default_channel)
        if self.channel not in self.channels:
            self.channels[self.channel] = set()            
        self.channels[self.channel].add(self)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

        self.broadcast(self.participants, "Someone left.")

def main():
    parse_command_line()
    router = sockjs.tornado.SockJSRouter(PubSub, '/pubsub')
    app = tornado.web.Application(
        [
            (r"/demo", DemoHandler),
        ] + router.urls,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()