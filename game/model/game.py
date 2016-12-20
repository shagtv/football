#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from datetime import datetime
from model.position import Position
from model.ball import Ball
from model.player import Player


class Game(object):
    field_width = 800
    field_height = 518

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

    def __init__(self):
        self.id = random.randrange(1000)
        self.dt = datetime.now().isoformat(sep=' ')[:-7]
        self.result = {
            'home': 0,
            'guest': 0,
        }
        self.players = set()
        self.ball = Ball(Game.field_width/2, Game.field_height/2)
        self.violation_count = 0
        self.violation_player = None
        self.pause = False

    def fill_players(self):
        for pos, i in enumerate(Game.positions):
            player = Player()
            player.x = int(Game.field_width * i.x)
            player.y = int(Game.field_height * i.y)
            player.position = pos
            player.pos_x = player.x
            player.pos_y = player.y
            player.speed = random.uniform(Player.speed - 0.5, Player.speed + 0.5)
            player.game = self
            self.players.add(player)

        for pos, i in enumerate(Game.positions):
            player = Player('guest')
            player.x = int(Game.field_width * (1 - i.x))
            player.y = int(Game.field_height * (1 - i.y))
            player.position = pos
            player.pos_x = player.x
            player.pos_y = player.y
            player.speed = random.uniform(Player.speed - 0.5, Player.speed + 0.5)
            player.game = self
            self.players.add(player)