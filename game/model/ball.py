#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Ball(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move_x = 0
        self.move_y = 0
        self.in_air = 0
        self.free = True
        self.own = None
        self.owner = None
        self.lastowner = None
        self.is_bad = False
        self.speed = 8.0
        
    def step(self):
        if self.lastowner:
            game = self.lastowner.game
        elif self.owner:
            game = self.owner.game
        else:
            from model.game import Game
            game = Game

        if self.x + self.move_x < 0:
            if game.field_height / 2 - 22 <= self.y <= game.field_height / 2 + 22:
                game.result['guest'] += 1
                game.violation_count = 30
            self.move_x = 0
            self.move_y = 0
            self.y = game.field_height / 2
            self.x = 20
        if self.y + self.move_y < 0:
            self.move_x = 0
            self.move_y = 0
            self.move_y = -self.move_y
            self.is_bad = True
        if self.x + self.move_x > game.field_width:
            if game.field_height / 2 - 22 <= self.y <= game.field_height / 2 + 22:
                game.result['home'] += 1
                game.violation_count = 30
            self.move_x = 0
            self.move_y = 0
            self.y = game.field_height / 2
            self.x = game.field_width - 20
        if self.y + self.move_y > game.field_height:
            self.move_x = 0
            self.move_y = 0
            self.move_y = -self.move_y
            self.is_bad = True

        if self.in_air > 0:
            self.in_air -= 1

        if self.free:
            self.x += self.move_x
            self.y += self.move_y

            self.move_x *= 0.97
            self.move_y *= 0.97