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

class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def distance(a, b):
        return float(sqrt((a.x - b.x)**2 + (a.y - b.y)**2))

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

        return (x, y)

    @staticmethod
    def min_dist_to_enemy(this, point):
        a = this.y - point.y
        b = point.x - this.x
        c = this.x * point.y - point.x * this.y
        d = ((this.x - point.x) ** 2 + (this.y - point.y) ** 2) ** 0.5
    
        min = Game.field_width

        if d == 0:
            return 0

        for i in GameWebSocketHandler.connections:
            if i.active and i.team != this.team:
                if (this.x > point.x and point.x <= i.x <= this.x) or (this.x <= point.x and this.x <= i.x <= point.x):
                    dist = abs((a * i.x + b * i.y + c) / d)
                    if dist < min:
                        min = dist
        return min

class Game(object):
    field_width = 800
    max_distance = 150
    field_height = 518
    player_size = 5
    speed = 2
    ball_speed = speed*4
    pause = False
    violation_player = None
    violation_count = 0
    msgs = []
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

class Player(object):
    teams = ('home', 'guest')

    def __init__(self):
        self.x = random.randrange(30, 700)
        self.y = random.randrange(30, 500)
        self.pos_x = 0
        self.pos_y = 0
        self.move_x = 0
        self.move_y = 0
        self.team = 'home'
        self.active = True
        self.speed = Game.speed
        self.name = str(random.randrange(100))
        self.role = 'bot'
        self.has_ball = False
        self.noattack = 0
        self.dopass = False
        self.dogoal = False

    def is_at(self, point):
        return Position.distance(self, point) <= Game.player_size*2

    def allow_pass(self, p1):
        flame_x = Game.frames[self.team].x
        half_width = Game.field_width / 2.0
        if p1.team == self.team and p1 is not self and p1.position != 0:
            if (flame_x == Game.field_width and self.x <= half_width) \
                    or (flame_x == Game.field_width and self.x >= half_width and p1.x >= Game.field_width / 2.0) \
                    or (flame_x == 0 and self.x >= half_width) \
                    or (flame_x == 0 and self.x <= half_width and p1.x <= Game.field_width / 2.0):
                return True
        return False

    def give_pass(self, player = None):
        best = None
        best_distance = None

        if player is None:
            for p1 in list(GameWebSocketHandler.connections):
                if p1 != self and p1.active and p1.team == self.team:
                    p1_distance = Position.distance(p1, Game.frames[p1.team])
                    if best_distance is None or p1_distance < best_distance:
                        best_distance = p1_distance
                        best = p1
        else:
            best = player

        Ball.lastowner = Ball.owner
        Ball.owner = None
        Ball.speed = Game.ball_speed

        Ball.free = True
        self.has_ball = False
        self.speed = Game.speed

        self.noattack = 5
        Ball.in_air = 5

        (Ball.move_x, Ball.move_y) = Position.move(Ball, best)
        return best

    def do_goal(self):
        Ball.lastowner = Ball.owner
        Ball.owner = None
        Ball.free = True
        Ball.speed = Game.ball_speed
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

    def find_open(self):
        best = None
        min = 0
        for p1 in list(GameWebSocketHandler.connections):
            if p1.active:
                if self.allow_pass(p1):
                    dist = Position.min_dist_to_enemy(self, p1)
                    if dist > min:
                        min = dist
                        best = p1
        return (best, min)

    def is_need_move(self):
        self_dist = Position.distance(self, Ball)
        closer_count = 0
        good_count = 0
        for p1 in list(GameWebSocketHandler.connections):
            if p1.active and p1.team == self.team and p1 is not self and self_dist < Game.field_width/2.0:
                dist = Position.distance(p1, Ball)
                if dist < self_dist:
                    closer_count += 1
                    if Ball.move_x == 0 or (p1.move_x >= 0 and Ball.move_x <= 0) or (p1.move_x <= 0 and Ball.move_x >= 0):
                        good_count += 1
        return closer_count < 3 and good_count < 2

    def check_violation(self):
        for p1 in list(GameWebSocketHandler.connections):
            if p1.active and p1.team != self.team and self.is_at(p1):
                if random.randrange(0, 15) == 2:
                    Game.violation_player = self
                    Game.violation_count = 50
                    Ball.move_x = 0
                    Ball.move_y = 0
                    text = '%s[%s] has violated the rules' % (p1.name, p1.team)
                    GameWebSocketHandler.send_msg(text, 'System')

    def move_to_home(self):
         if self.is_at(Position(self.pos_x, self.pos_y)):
             return (0, 0)
         return Position.move(self, Position(self.pos_x, self.pos_y))

class Ball(object):
    x = Game.field_width/2
    y = Game.field_height/2
    free = True
    own = None
    owner = None
    lastowner = None
    move_x = 0
    move_y = 0
    speed = Game.ball_speed
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
        self.name = 'P'
        self.role = 'player'
        self.active = False

        for msg in Game.msgs:
            self.write_message(msg)
        GameWebSocketHandler.connections.add(self)

    def on_close(self):
        GameWebSocketHandler.send_msg(self.name + ' left game', 'System')
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
                    player.speed = random.uniform(Game.speed - 0.5, Game.speed + 0.5)

                    GameWebSocketHandler.connections.add(player)
                for pos, i in enumerate(Game.positions):
                    player = Player()
                    player.x = int(Game.field_width*(1 - i.x))
                    player.y = int(Game.field_height*(1 - i.y))
                    player.team = 'guest'
                    player.position = pos
                    player.pos_x = player.x
                    player.pos_y = player.y
                    player.speed = random.uniform(Game.speed - 0.5, Game.speed + 0.5)

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
            if self.name != data['name']:
                if 'first' in data:
                    text = data['name'] + ' join game'
                else:
                    text = self.name + ' change name to ' + data['name']
                GameWebSocketHandler.send_msg(text, 'System')
            self.name = data['name']

        elif data['command'] == 'pass':
            self.dopass = True

        elif data['command'] == 'goal':
            self.dogoal = True

        elif data['command'] == 'msg':
            GameWebSocketHandler.send_msg(data['msg'], self.name)

    @staticmethod
    def send_msg(text, author):
        msg = {
            'command': 'msg',
            'msg': text,
            'author': author,
            'dt': datetime.now().isoformat(sep=' ')[11:-7]
        }

        Game.msgs.append(msg)

        for i in GameWebSocketHandler.connections:
            if isinstance(i, GameWebSocketHandler):
                try:
                    i.write_message(msg)
                except:
                    pass

    @staticmethod
    def period_run():
        if Game.pause:
            return None

        if Game.violation_count > 0:
            Game.violation_count -= 1

        players = []
        if GameWebSocketHandler.started:
            for p in list(GameWebSocketHandler.connections):
                if p.active:
                    if Game.violation_count > 0:
                        Ball.move_x = 0
                        Ball.move_y = 0
                        if Game.violation_player == p:
                            (p.move_x, p.move_y) = Position.move(p, Ball)
                        else:
                            (p.move_x, p.move_y) = p.move_to_home()

                    elif p.noattack > 0:
                        p.noattack -= 1

                    elif p.dopass:
                        p.give_pass()
                        p.dogoal = False

                    elif p.dogoal:
                        p.do_goal()
                        p.dogoal = False

                    elif Ball.in_air == 0 and p.is_at(Ball) and not p.has_ball and (not Ball.is_bad or Ball.lastowner.team != p.team):
                        last_owner = Ball.owner
                        if not last_owner or random.randrange(3) == 1:
                            if last_owner:
                                last_owner.has_ball = False
                                last_owner.move_x = 0
                                last_owner.move_y = 0
                                last_owner.noattack = 5
                            Ball.free = False

                            if Ball.is_bad:
                                Game.violation_count = 30

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
                                if p.is_need_move():
                                    (p.move_x, p.move_y) = Position.move(p, Position(Ball.x + Ball.move_y, Ball.y + Ball.move_y))
                                else:
                                    (p.move_x, p.move_y) = p.move_to_home()
                            else:
                                p.check_violation()
                                open_player, dist = p.find_open()
                                if p.min_dist_to_enemy() < 50 and open_player and dist > 10:
                                    p.give_pass(open_player)
                                    p.noattack = 5
                                else:
                                    (p.move_x, p.move_y) = Position.move(p, Game.frames[p.team])
                                    frame_pos = Game.frames[p.team]
                                    frame_distance = Position.distance(p, frame_pos)
                                    finish_distance = Position.distance(p, Position(frame_pos.x, p.y))
                                    if frame_distance < 100 or finish_distance < 100 or Position.min_dist_to_enemy(p, frame_pos) > 10:
                                        p.do_goal()
                                    elif frame_distance < 50 or finish_distance < 50:
                                        p.do_goal()
                    else:
                        if p.role == 'bot':
                            if (p.position == 0 and Position.distance(p, Ball) < 100) or (p.position != 0 and p.is_need_move()):
                                (p.move_x, p.move_y) = Position.move(p, Position(Ball.x + Ball.move_y, Ball.y + Ball.move_y))
                            else:
                                (p.move_x, p.move_y) = p.move_to_home()

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
                    Game.violation_count = 30
                    GameWebSocketHandler.send_msg(Ball.lastowner.name + '(guest) has scored a goal', 'System')
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
                    Game.violation_count = 30
                    GameWebSocketHandler.send_msg(Ball.lastowner.name + '(home) has scored a goal', 'System')
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

                Ball.move_x *= 0.97
                Ball.move_y *= 0.97

        msg = {
            'command': 'draw',
            'players': players,
            'ball': [Ball.x, Ball.y],
            'result': Game.result,
            'ccu': len([i for i in GameWebSocketHandler.connections if isinstance(i, GameWebSocketHandler)])
        }

        for i in GameWebSocketHandler.connections:
            if isinstance(i, GameWebSocketHandler):
                try:
                    i.write_message(msg)
                except:
                    pass

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
