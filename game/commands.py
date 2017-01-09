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

    @staticmethod
    def start(self, id):
        for game in application.games:
            if game.id == id:
                game.pause = False

    @staticmethod
    def pause(self, id):
        for game in application.games:
            if game.id == id:
                game.pause = True

    @staticmethod
    def join(self, id):
        for game in application.games:
            if game.id == id:
                for p in game.players:
                    if p.conn is None:
                        p.conn = self
                        p.name = p.name + '*'
                        break

    @staticmethod
    def leave(self, id):
        for game in application.games:
            if game.id == id:
                for p in game.players:
                    if self == p.conn:
                        p.conn = None
                        p.name = p.name.replace('*', '')
                        break

    @staticmethod
    def move(self, data):
        for game in application.games:
            if game.id == data['id']:
                for p in game.players:
                    if self == p.conn:
                        p.move_x = data['moveX']
                        p.move_y = data['moveY']
                        break

    @staticmethod
    def dopass(self, id):
        for game in application.games:
            if game.id == id:
                for p in game.players:
                    if self == p.conn:
                        p.dopass = True
                        break

    @staticmethod
    def dogoal(self, id):
        for game in application.games:
            if game.id == id:
                for p in game.players:
                    if self == p.conn:
                        p.dogoal = True
                        break