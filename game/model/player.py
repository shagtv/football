#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

from model.Position import Position

class Player(object):
    speed = 2.0
    size = 5

    def __init__(self, team='home'):
        self.x = random.randrange(30, 700)
        self.y = random.randrange(30, 500)
        self.pos_x = 0
        self.pos_y = 0
        self.move_x = 0
        self.move_y = 0
        self.team = team
        self.name = str(random.randrange(100))
        self.conn = None
        self.noattack = 0
        self.has_ball = False
        self.game = None
        self.dopass = False
        self.dogoal = False

    def is_at(self, point):
        return Position.distance(self, point) <= Player.size*2

    def allow_pass(self, p1):
        flame_x = self.game.frames[self.team].x
        half_width = self.game.field_width / 2.0
        if p1.team == self.team and p1 is not self and p1.position != 0:
            if (flame_x == self.game.field_width and self.x <= half_width) \
                    or (flame_x == self.game.field_width and self.x >= half_width and p1.x >= self.game.field_width / 2.0) \
                    or (flame_x == 0 and self.x >= half_width) \
                    or (flame_x == 0 and self.x <= half_width and p1.x <= self.game.field_width / 2.0):
                return True
        return False

    def do_goal(self):
        self.game.ball.lastowner = self.game.ball.owner
        self.game.ball.owner = None
        self.game.ball.free = True
        self.has_ball = False
        (self.game.ball.move_x, self.game.ball.move_y) = Position.move(self.game.ball, self.game.frames[self.team])
        self.move_x = 0
        self.move_y = 0
        self.noattack = 3

    def give_pass(self, player = None):
        best = None
        best_distance = None

        if player is None:
            for p1 in list(self.game.players):
                if p1 != self and p1.team == self.team:
                    p1_distance = Position.distance(p1, self.game.frames[p1.team])
                    if best_distance is None or p1_distance < best_distance:
                        best_distance = p1_distance
                        best = p1
        else:
            best = player

        self.game.ball.lastowner = self.game.ball.owner
        self.game.ball.owner = None

        self.game.ball.free = True
        self.has_ball = False

        self.noattack = 5
        self.game.ball.in_air = 5

        (self.game.ball.move_x, self.game.ball.move_y) = Position.move(self.game.ball, best)
        return best

    def min_dist_to_enemy(self):
        best_distance = None

        for p1 in list(self.game.players):
            if p1.team != self.team:
                p1_distance = Position.distance(p1, self)
                if best_distance is None or p1_distance < best_distance:
                    best_distance = p1_distance

        return best_distance

    def find_open(self):
        best = None
        min = 0
        for p1 in list(self.game.players):
            if self.allow_pass(p1):
                dist = Position.min_dist_to_enemy(self, p1)
                if dist > min:
                    min = dist
                    best = p1
        return (best, min)

    def is_need_move(self):
        self_dist = Position.distance(self, self.game.ball)
        closer_count = 0
        good_count = 0
        for p1 in list(self.game.players):
            if p1.team == self.team and p1 is not self and self_dist < self.game.field_width/2.0:
                dist = Position.distance(p1, self.game.ball)
                if dist < self_dist:
                    closer_count += 1
                    if self.game.ball.move_x == 0 or (p1.move_x >= 0 and self.game.ball.move_x <= 0) or (p1.move_x <= 0 and self.game.ball.move_x >= 0):
                        good_count += 1
        return closer_count < 3 and good_count < 2

    def move_to_home(self):
         if self.is_at(Position(self.pos_x, self.pos_y)):
             return (0, 0)
         return Position.move(self, Position(self.pos_x, self.pos_y))

    def check_violation(self):
        for p1 in list(self.game.players):
            if p1.team != self.team and self.is_at(p1):
                if random.randrange(0, 20) == 2:
                    self.game.violation_player = self
                    self.game.violation_count = 50
                    self.game.ball.move_x = 0
                    self.game.ball.move_y = 0
