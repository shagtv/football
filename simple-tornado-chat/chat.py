import json
import os.path

import random
from datetime import datetime
from math import sqrt, acos, cos, sin
from time import sleep
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tornado.gen

from tornado.options import define, options, parse_command_line

define('port', default=8000, help='run on the given port', type=int)

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def distance(a, b):
        return int(sqrt((a.x - b.x)**2 + (a.y - b.y)**2))

    @staticmethod
    def move(this, point):
        distance = Position.distance(this, point)
        if distance == 0:
            return (0, 0)

        try:
            v = acos((abs(this.x - point.x) / distance))
        except:
            return (0, 0)

        x = this.speed * cos(v)
        y = this.speed * sin(v)

        if point.x >= this.x and point.y < this.y:
            y *= -1
        elif point.x < this.x and point.y >= this.y:
            x *= -1
        elif point.x < this.x and point.y < this.y:
            x *= -1
            y *= -1

        return (int(x), int(y))

class Game:
    field_width = 800
    max_distance = 150
    field_height = 518
    player_size = 5
    speed = 2
    pause = False

    result = {
        'home': 0,
        'guest': 0,
    }

    frames = {
        'home': Position(field_width, field_height / 2),
        'guest': Position(0, field_height / 2),
    }

    positions = [
        Position(0.05, 0.5),
        Position(0.8, 0.32),
        Position(0.8, 0.72),
        Position(0.7, 0.12),
        Position(0.7, 0.92),
        Position(0.6, 0.32),
        Position(0.6, 0.72),
        Position(0.4, 0.32),
        Position(0.4, 0.72),
        Position(0.2, 0.32),
        Position(0.2, 0.72),
    ]

class Player:
    teams = ('home', 'guest')

    def __init__(self):
        self.x = random.randrange(30, 700)
        self.y = random.randrange(30, 500)
        self.move_x = 0
        self.move_y = 0
        self.team = 'home'
        self.active = True
        self.speed = Game.speed
        self.name = 'Bot' + str(random.randrange(1000))
        self.role = 'bot'
        self.has_ball = False
        self.noattack = 0
        self.dopass = False
        self.dogoal = False

    def is_at(self, point):
        return Position.distance(self, point) <= Game.player_size*2

    def give_pass(self):
        best = None
        best_distance = None

        for p1 in list(GameWebSocketHandler.connections):
            if p1 != self and p1.active and p1.team == self.team:
                p1_distance = Position.distance(p1, Game.frames[p1.team])
                if best_distance is None or p1_distance < best_distance:
                    best_distance = p1_distance
                    best = p1

        Ball.owner = None
        Ball.free = True
        self.has_ball = False
        self.speed = Game.speed
        self.noattack = 3

        if best_distance >= Position.distance(self, Game.frames[self.team]):
            (Ball.move_x, Ball.move_y) = Position.move(Ball, Game.frames[self.team])
            return None
        else:
            Ball.in_air = 10
            (Ball.move_x, Ball.move_y) = Position.move(Ball, best)
            return best

    def do_goal(self):
        Ball.owner = None
        Ball.free = True
        self.has_ball = False
        self.speed = Game.speed
        (Ball.move_x, Ball.move_y) = Position.move(Ball, Game.frames[self.team])
        self.move_x = 0
        self.move_y = 0
        self.noattack = 3

    def min_dist_to_enemy(self):
        best_distance = None

        for p1 in list(GameWebSocketHandler.connections):
            if p1.active and p1.team != self.team:
                p1_distance = Position.distance(p1, self)
                if best_distance is None or p1_distance < best_distance:
                    best_distance = p1_distance

        return best_distance

class Ball:
    x = Game.field_width/2
    y = Game.field_height/2
    free = True
    own = None
    owner = None
    move_x = 0
    move_y = 0
    speed = Game.speed*2
    in_air = 0
    is_bad = False

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

class GameWebSocketHandler(tornado.websocket.WebSocketHandler, tornado.web.RequestHandler, Player):
    connections = set()
    started = False

    def open(self):
        teams = ('home', 'guest')

        self.team = Player.teams[random.randrange(0, 2)]
        self.name = 'Player'
        self.role = 'player'
        self.active = False

        GameWebSocketHandler.connections.add(self)

    def on_close(self):
        GameWebSocketHandler.connections.remove(self)

    def on_message(self, msg):
        data = json.loads(msg)

        if data['command'] == 'move':
            self.move_x = int(data['moveX'])
            self.move_y = int(data['moveY'])
        elif data['command'] == 'join':
            if not self.active:
                for p in list(GameWebSocketHandler.connections):
                    if p.active and p.role == 'bot':
                        self.team = p.team
                        self.x = p.x
                        self.y = p.y
                        self.position = p.position
                        self.pos_x = p.pos_x
                        self.pos_y = p.pos_y
                        self.has_ball = p.has_ball
                        GameWebSocketHandler.connections.remove(p)
                        self.active = True
                        break
        elif data['command'] == 'leave':
            if self.active:
                self.active = False
                player = Player()
                player.team = self.team
                player.x = self.x
                player.y = self.y
                player.position = self.position
                player.pos_x = self.pos_x
                player.pos_y = self.pos_y
                GameWebSocketHandler.connections.add(player)

        elif data['command'] == 'pause':
            Game.pause = True

        elif data['command'] == 'start':
            Game.pause = False
            if not GameWebSocketHandler.started:
                GameWebSocketHandler.started = True
                for pos, i in enumerate(Game.positions):
                    player = Player()
                    player.x = int(Game.field_width*i.x)
                    player.y = int(Game.field_height*i.y)
                    player.position = pos
                    player.pos_x = player.x
                    player.pos_y = player.y
                    GameWebSocketHandler.connections.add(player)
                for pos, i in enumerate(Game.positions):
                    player = Player()
                    player.x = int(Game.field_width*(1 - i.x))
                    player.y = int(Game.field_height*(1 - i.y))
                    player.team = 'guest'
                    player.position = pos
                    player.pos_x = player.x
                    player.pos_y = player.y
                    GameWebSocketHandler.connections.add(player)

        elif data['command'] == 'stop':
            if GameWebSocketHandler.started:
                Ball.x = Game.field_width/2
                Ball.y = Game.field_height/2
                Ball.move_x = 0
                Ball.move_y = 0
                Game.result['home'] = 0
                Game.result['guest'] = 0
                GameWebSocketHandler.started = False
                for p in list(GameWebSocketHandler.connections):
                    if p.role == 'bot':
                        GameWebSocketHandler.connections.remove(p)
                    else:
                        p.active = False

        elif data['command'] == 'save-name':
            self.name = data['name']

        elif data['command'] == 'pass':
            self.dopass = True

        elif data['command'] == 'goal':
            self.dogoal = True

        elif data['command'] == 'msg':
            msg = {
                'command': 'msg',
                'msg': data['msg'],
                'author': self.name,
                'dt': datetime.now().isoformat(sep=' ')[11:-7]
            }
            for i in GameWebSocketHandler.connections:
                if isinstance(i, GameWebSocketHandler):
                    i.write_message(msg)



    @staticmethod
    def period_run():
        if Game.pause:
            return None

        players = []
        if GameWebSocketHandler.started:
            for p in list(GameWebSocketHandler.connections):
                if p.active:
                    if p.noattack > 0:
                        p.noattack -= 1

                    elif p.dopass:
                        p.give_pass()
                        p.dogoal = False

                    elif p.dogoal:
                        p.do_goal()
                        p.dogoal = False

                    elif Ball.in_air == 0 and p.is_at(Ball) and not p.has_ball:
                        last_owner = Ball.owner
                        if not last_owner or random.randrange(2) == 1:
                            if last_owner:
                                last_owner.has_ball = False
                                last_owner.move_x = 0
                                last_owner.move_y = 0
                                last_owner.noattack = 3
                                GameWebSocketHandler.connections.add(last_owner)
                            Ball.free = False
                            Ball.is_bad = False
                            Ball.owner = p
                            Ball.own = p.team
                            p.has_ball = True

                            if p.role == 'bot':
                                if p.position == 0:
                                    p.give_pass()
                                    p.noattack = 3
                                else:
                                    (p.move_x, p.move_y) = Position.move(p, Game.frames[p.team])
                    elif p.team == Ball.own and not Ball.free:
                        if p.role == 'bot':
                            if p is not Ball.owner:
                                if Position.distance(p, Ball) < Game.max_distance/2:
                                    (p.move_x, p.move_y) = Position.move(p, Ball)
                                elif p.position in (8, 9):
                                    (p.move_x, p.move_y) = Position.move(p, Game.frames[p.team])
                                else:
                                    (p.move_x, p.move_y) = Position.move(p, Position(p.pos_x, p.pos_y))
                            else:
                                if p.min_dist_to_enemy() < 50:
                                    p.give_pass()
                                    p.noattack = 5
                                else:
                                    (p.move_x, p.move_y) = Position.move(p, Game.frames[p.team])
                                    frame_pos = Game.frames[p.team]
                                    frame_distance = Position.distance(p, frame_pos)
                                    finish_distance = Position.distance(p, Position(frame_pos.x, p.y))
                                    if frame_distance < 100 or finish_distance < 50:
                                        p.do_goal()
                    else:
                        if p.role == 'bot':
                            if p.position != 0 or Position.distance(p, Ball) < 200:
                                (p.move_x, p.move_y) = Position.move(p, Position(Ball.x + Ball.move_y, Ball.y + Ball.move_y))
                            else:
                                (p.move_x, p.move_y) = Position.move(p, Position(p.pos_x, p.pos_y))

                    if p.role == 'bot':
                        distance = Position.distance(p, Position(p.pos_x, p.pos_y))
                        if distance + Game.player_size >= Game.max_distance and (not Ball.is_bad or Ball.own == p.team):
                            if p.has_ball:
                                p.give_pass()
                            (p.move_x, p.move_y) = Position.move(p, Position(p.pos_x, p.pos_y))

                    p.x += p.move_x
                    p.y += p.move_y

                    if p.x - Game.player_size < 0:
                        p.x = Game.player_size
                    if p.y - Game.player_size < 0:
                        p.y = Game.player_size
                    if p.x + Game.player_size > Game.field_width:
                        p.x = Game.field_width - Game.player_size
                    if p.y + Game.player_size > Game.field_height:
                        p.y = Game.field_height - Game.player_size

                    if p.has_ball:
                        Ball.x = p.x
                        Ball.y = p.y

                    players.append([p.x, p.y, p.speed, p.team, p.name])

            if Ball.x + Ball.move_x < 0:
                if Ball.y <= Game.field_height/2 + 22 and Ball.y >= Game.field_height/2 - 22:
                    Game.result['guest'] += 1
                Ball.move_x = 0
                Ball.move_y = 0
                Ball.y = Game.field_height/2
                Ball.x = 20
            if Ball.y + Ball.move_y < 0:
                Ball.move_x = 0
                Ball.move_y = 0
                Ball.move_y = -Ball.move_y
                Ball.is_bad = True
            if Ball.x + Ball.move_x > Game.field_width:
                if Ball.y <= Game.field_height/2 + 22 and Ball.y >= Game.field_height/2 - 22:
                    Game.result['home'] += 1
                Ball.move_x = 0
                Ball.move_y = 0
                Ball.y = Game.field_height / 2
                Ball.x = Game.field_width - 20
            if Ball.y + Ball.move_y > Game.field_height:
                Ball.move_x = 0
                Ball.move_y = 0
                Ball.move_y = -Ball.move_y
                Ball.is_bad = True

            if Ball.in_air > 0:
                Ball.in_air -= 1

            if Ball.free:
                Ball.x += Ball.move_x
                Ball.y += Ball.move_y
        msg = {'command': 'draw', 'players': players, 'ball': [Ball.x, Ball.y], 'result': Game.result}

        for i in GameWebSocketHandler.connections:
            if isinstance(i, GameWebSocketHandler):
                i.write_message(msg)

def main():
    parse_command_line()
    app = Application()
    app.listen(options.port)

    loop = tornado.ioloop.IOLoop.instance()
    period_cbk = tornado.ioloop.PeriodicCallback(GameWebSocketHandler.period_run, 50, loop)
    period_cbk.start()
    loop.start()


if __name__ == '__main__':
    main()
