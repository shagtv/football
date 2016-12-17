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
