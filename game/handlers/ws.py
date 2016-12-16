#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from tornado import web, websocket

import application
from commands import Commands


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


