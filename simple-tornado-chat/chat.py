import json
import os.path

import random

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tornado.gen

from tornado.options import define, options, parse_command_line

define('port', default=8000, help='run on the given port', type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', GameHandler),
            (r'/ws', GameWebSocketHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class GameHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('game.html')

class GameWebSocketHandler(tornado.websocket.WebSocketHandler, tornado.web.RequestHandler):
    connections = set()

    def open(self):
        self.x = random.randrange(30, 700)
        self.y = random.randrange(30, 500)
        GameWebSocketHandler.connections.add(self)

    def on_close(self):
        GameWebSocketHandler.connections.remove(self)

    def on_message(self, msg):
        data = json.loads(msg)

        players = []
        for i in GameWebSocketHandler.connections:
            if  i == self:
                i.x += data['moveX']
                i.y += data['moveY']
            players.append([i.x, i.y])

        for i in GameWebSocketHandler.connections:
            i.write_message({'command': 'check', 'players': players})

    def send_messages(self, msg):
        for conn in self.connections:
            #conn.write_message({'name': self.current_user, 'msg': msg})
            conn.write_message({'name': 'shagtv', 'msg': msg})

def main():
    parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
