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
                p.step()

            game.ball.step()
