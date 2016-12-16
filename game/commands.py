#!/usr/bin/env python
# -*- coding: utf-8 -*-

import application
from model.game import Game


class Commands(object):
    @staticmethod
    def game_list(conn):
        conn.write_message({
            'command': 'game-list',
            'games': [(game.id, game.dt) for game in application.games]
        })

    @staticmethod
    def create(conn):
        game = Game()
        application.games.append(game)
