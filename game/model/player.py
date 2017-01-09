#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from model.position import Position


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
        self.position = 0

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

    def step(self):
        if self.game.violation_count > 0:
            self.game.ball.move_x = 0
            self.game.ball.move_y = 0
            if self.game.violation_player == self:
                (self.move_x, self.move_y) = Position.move(self, self.game.ball)
            else:
                (self.move_x, self.move_y) = self.move_to_home()

        elif self.noattack > 0:
            self.noattack -= 1

        elif self.dopass:
            self.give_pass()
            self.dogoal = False

        elif self.dogoal:
            self.do_goal()
            self.dogoal = False

        elif self.game.ball.in_air == 0 and self.is_at(self.game.ball) and not self.has_ball and (
            not self.game.ball.is_bad or self.game.ball.lastowner.team != self.team):
            last_owner = self.game.ball.owner
            if not last_owner or random.randrange(3) == 1:
                if last_owner:
                    last_owner.has_ball = False
                    last_owner.move_x = 0
                    last_owner.move_y = 0
                    last_owner.noattack = 5
                self.game.ball.free = False

                if self.game.ball.is_bad:
                    self.game.violation_count = 30

                self.game.ball.is_bad = False
                self.game.ball.owner = self
                self.game.ball.own = self.team
                self.has_ball = True

                if self.conn is None:
                    if self.position == 0:
                        self.give_pass()
                        self.noattack = 3
                    else:
                        (self.move_x, self.move_y) = Position.move(self, self.game.frames[self.team])
        elif self.team == self.game.ball.own and not self.game.ball.free:
            if self.conn is None:
                if self is not self.game.ball.owner:
                    if self.is_need_move():
                        (self.move_x, self.move_y) = Position.move(self, self.game.ball)
                    else:
                        (self.move_x, self.move_y) = self.move_to_home()
                else:
                    self.check_violation()
                    open_player, dist = self.find_open()
                    if self.min_dist_to_enemy() < 50 and open_player and dist > 20:
                        self.give_pass(open_player)
                        self.noattack = 5
                    else:
                        (self.move_x, self.move_y) = Position.move(self, self.game.frames[self.team])

                        frame_pos = self.game.frames[self.team]
                        frame_distance = Position.distance(self, frame_pos)
                        if frame_distance < 100 or Position.min_dist_to_enemy(self, frame_pos) > 10:
                            self.do_goal()
                        elif frame_distance < 50:
                            self.do_goal()
        else:
            if self.conn is None:
                if (self.position == 0 and Position.distance(self, self.game.ball) < 100) \
                        or (self.position != 0 and self.is_need_move()):
                    (self.move_x, self.move_y) = Position.move(self, self.game.ball)
                else:
                    (self.move_x, self.move_y) = self.move_to_home()

        self.x += self.move_x
        self.y += self.move_y

        if self.x < Player.size:
            self.x = Player.size
        if self.y < Player.size:
            self.y = Player.size
        if self.x > self.game.field_width - Player.size:
            self.x = self.game.field_width - Player.size
        if self.y > self.game.field_height - Player.size:
            self.y = self.game.field_height - Player.size

        if self.has_ball:
            self.game.ball.x = self.x
            self.game.ball.y = self.y