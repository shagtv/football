#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import random

from tornado import web, websocket
import application
from commands import Commands
from model.Position import Position
from model.game import Game
from model.player import Player


class GameHandler(websocket.WebSocketHandler, web.RequestHandler):
    def data_received(self, chunk):
        pass

    def open(self):
        application.connections.add(self)

    def on_close(self):
        application.connections.remove(self)

    def on_message(self, msg):
        data = json.loads(msg)
        if 'command' in data:
            command = data['command']
            if command == 'game-list': Commands.game_list(self)
            elif command == 'create': Commands.create(self)
            elif command == 'game-info': Commands.game_info(self, data['id'])

    @staticmethod
    def period_run():
        for game in application.games:
            if game.pause:
                continue

            if game.violation_count > 0:
                game.violation_count -= 1

            for p in list(game.players):
                if game.violation_count > 0:
                    game.ball.move_x = 0
                    game.ball.move_y = 0
                    if game.violation_player == p:
                        (p.move_x, p.move_y) = Position.move(p, game.ball)
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

                elif game.ball.in_air == 0 and p.is_at(game.ball) and not p.has_ball and (not game.ball.is_bad or game.ball.lastowner.team != p.team):
                    last_owner = game.ball.owner
                    if not last_owner or random.randrange(3) == 1:
                        if last_owner:
                            last_owner.has_ball = False
                            last_owner.move_x = 0
                            last_owner.move_y = 0
                            last_owner.noattack = 5
                        game.ball.free = False

                        if game.ball.is_bad:
                            game.violation_count = 30

                        game.ball.is_bad = False
                        game.ball.owner = p
                        game.ball.own = p.team
                        p.has_ball = True

                        if p.conn is None:
                            if p.position == 0:
                                p.give_pass()
                                p.noattack = 3
                            else:
                                (p.move_x, p.move_y) = Position.move(p, game.frames[p.team])
                elif p.team == game.ball.own and not game.ball.free:
                    if p.conn is None:
                        if p is not game.ball.owner:
                            if p.is_need_move():
                                (p.move_x, p.move_y) = Position.move(p, Position(game.ball.x + game.ball.move_y, game.ball.y + game.ball.move_y))
                            else:
                                (p.move_x, p.move_y) = p.move_to_home()
                        else:
                            p.check_violation()
                            open_player, dist = p.find_open()
                            if p.min_dist_to_enemy() < 50 and open_player and dist > 10:
                                p.give_pass(open_player)
                                p.noattack = 5
                            else:
                                (p.move_x, p.move_y) = Position.move(p, game.frames[p.team])

                                frame_pos = game.frames[p.team]
                                frame_distance = Position.distance(p, frame_pos)
                                finish_distance = Position.distance(p, Position(frame_pos.x, p.y))
                                if frame_distance < 100 or finish_distance < 100 or Position.min_dist_to_enemy(p, frame_pos) > 10:
                                    p.do_goal()
                                elif frame_distance < 50 or finish_distance < 50:
                                    p.do_goal()
                else:
                    if p.conn is None:
                        if (p.position == 0 and Position.distance(p, game.ball) < 100) or (p.position != 0 and p.is_need_move()):
                            (p.move_x, p.move_y) = Position.move(p, Position(game.ball.x + game.ball.move_y, game.ball.y + game.ball.move_y))
                        else:
                            (p.move_x, p.move_y) = p.move_to_home()

                p.x += p.move_x
                p.y += p.move_y

                if p.x - Player.size < 0:
                    p.x = Player.size
                if p.y - Player.size < 0:
                    p.y = Player.size
                if p.x + Player.size > Game.field_width:
                    p.x = Game.field_width - Player.size
                if p.y + Player.size > Game.field_height:
                    p.y = Game.field_height - Player.size

                if p.has_ball:
                    game.ball.x = p.x
                    game.ball.y = p.y

            if game.ball.x + game.ball.move_x < 0:
                if game.ball.y <= Game.field_height/2 + 22 and game.ball.y >= Game.field_height/2 - 22:
                    game.result['guest'] += 1
                    game.violation_count = 30
                game.ball.move_x = 0
                game.ball.move_y = 0
                game.ball.y = Game.field_height/2
                game.ball.x = 20
            if game.ball.y + game.ball.move_y < 0:
                game.ball.move_x = 0
                game.ball.move_y = 0
                game.ball.move_y = -game.ball.move_y
                game.ball.is_bad = True
            if game.ball.x + game.ball.move_x > Game.field_width:
                if game.ball.y <= Game.field_height/2 + 22 and game.ball.y >= Game.field_height/2 - 22:
                    game.result['home'] += 1
                game.ball.move_x = 0
                game.ball.move_y = 0
                game.ball.y = Game.field_height / 2
                game.ball.x = Game.field_width - 20
            if game.ball.y + game.ball.move_y > Game.field_height:
                game.ball.move_x = 0
                game.ball.move_y = 0
                game.ball.move_y = -game.ball.move_y
                game.ball.is_bad = True

            if game.ball.in_air > 0:
                game.ball.in_air -= 1

            if game.ball.free:
                game.ball.x += game.ball.move_x
                game.ball.y += game.ball.move_y

                game.ball.move_x *= 0.97
                game.ball.move_y *= 0.97

