#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import random
import threading

from tornado import web, websocket
import application
from commands import Commands
from model.position import Position
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
            elif command == 'start': Commands.start(self, data['id'])
            elif command == 'pause': Commands.pause(self, data['id'])
            elif command == 'join': Commands.join(self, data['id'])
            elif command == 'leave': Commands.leave(self, data['id'])
            elif command == 'move': Commands.move(self, data)

    @staticmethod
    def period_run():
        for game in application.games:
            if game.pause:
                continue

            if game.violation_count > 0:
                game.violation_count -= 1

            for p in list(game.players):
                p.start()
                p.join()

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


class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print(1)
        