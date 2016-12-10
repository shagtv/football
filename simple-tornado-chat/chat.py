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

class Bot:
    def __init__(self, team, name):
        self.x = random.randrange(30, 700)
        self.y = random.randrange(30, 500)
        self.move_x = 0
        self.move_y = 0
        self.team = team
        self.active = True
        self.speed = 3
        self.name = name

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
    started = False

    def open(self):
        teams = ('home', 'guest')

        self.x = random.randrange(30, 700)
        self.y = random.randrange(30, 500)
        self.speed = 3
        self.team = teams[random.randrange(0, 2)]
        self.move_x = 0
        self.move_y = 0
        self.active = False
        self.name = 'noname'

        GameWebSocketHandler.connections.add(self)

    def on_close(self):
        GameWebSocketHandler.connections.remove(self)

    def on_message(self, msg):
        data = json.loads(msg)

        if data['command'] == 'move':
            self.move_x = data['moveX']
            self.move_y = data['moveY']
            GameWebSocketHandler.connections.add(self)
        elif data['command'] == 'join':
            if not self.active:
                for p in list(GameWebSocketHandler.connections):
                    if p.active and isinstance(p, Bot):
                        self.team = p.team
                        GameWebSocketHandler.connections.remove(p)
                        self.active = True
                        GameWebSocketHandler.connections.add(self)
                        break
        elif data['command'] == 'leave':
            if self.active:
                self.active = False
                GameWebSocketHandler.connections.add(self)
                player = Bot(self.team, 'Bot' + str(random.randrange(100)))
                GameWebSocketHandler.connections.add(player)

        elif data['command'] == 'start':
            if not GameWebSocketHandler.started:
                GameWebSocketHandler.started = True
                for i in range(10):
                    player = Bot('home', 'Bot' + str(i))
                    GameWebSocketHandler.connections.add(player)
                for i in range(10):
                    player = Bot('guest', 'Bot' + str(i + 10))
                    GameWebSocketHandler.connections.add(player)

        elif data['command'] == 'stop':
            if GameWebSocketHandler.started:
                GameWebSocketHandler.started = False
                for p in list(GameWebSocketHandler.connections):
                    if isinstance(p, Bot):
                        GameWebSocketHandler.connections.remove(p)
                    else:
                        p.active = False
                        GameWebSocketHandler.connections.add(self)

        elif data['command'] == 'save-name':
            self.name = data['name']
            GameWebSocketHandler.connections.add(self)

    @staticmethod
    def period_run():
        players = []
        if GameWebSocketHandler.started:
            for p in GameWebSocketHandler.connections:
                if p.active:
                    p.x += p.move_x
                    p.y += p.move_y
                    players.append([p.x, p.y, p.speed, p.team, p.name])

        msg = {'command': 'draw', 'players': players}

        for i in GameWebSocketHandler.connections:
            if isinstance(i, GameWebSocketHandler):
                i.write_message(msg)

def main():
    parse_command_line()
    app = Application()
    app.listen(options.port)

    loop = tornado.ioloop.IOLoop.instance()
    period_cbk = tornado.ioloop.PeriodicCallback(GameWebSocketHandler.period_run, 20, loop)
    period_cbk.start()
    loop.start()


if __name__ == '__main__':
    main()
