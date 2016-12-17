#!/usr/bin/env python
# -*- coding: utf-8 -*-

import application
from model.game import Game


class Commands(object):
    @staticmethod
    def game_list(conn):
        conn.write_message({
            'command': 'game-list',
            'games': [(game.id, game.dt, game.result) for game in application.games]
        })

    @staticmethod
    def create(conn):
        game = Game()
        game.fill_players()
        application.games.append(game)

    @staticmethod
    def game_info(self, id):
        for game in application.games:
            if game.id == id:
                players = []

                for p in game.players:
                    players.append([p.x, p.y, p.team, p.name])

                msg = {
                    'command': 'draw',
                    'players': players,
                    'ball': [game.ball.x, game.ball.y],
                    'result': game.result,
                }
                self.write_message(msg)
