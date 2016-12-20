#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sin, cos, acos, sqrt


class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def distance(a, b):
        return float(sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2))

    @staticmethod
    def move(this, point):
        distance = Position.distance(this, point)
        if distance == 0:
            return (0, 0)

        try:
            v = acos((abs(this.x - point.x) / distance))
        except:
            return (0, 0)

        x = this.speed * cos(v)
        y = this.speed * sin(v)

        if point.x >= this.x and point.y < this.y:
            y *= -1
        elif point.x < this.x and point.y >= this.y:
            x *= -1
        elif point.x < this.x and point.y < this.y:
            x *= -1
            y *= -1

        return (x, y)

    @staticmethod
    def min_dist_to_enemy(this, point):
        a = this.y - point.y
        b = point.x - this.x
        c = this.x * point.y - point.x * this.y
        d = ((this.x - point.x) ** 2 + (this.y - point.y) ** 2) ** 0.5

        min = this.game.field_width

        if d == 0:
            return 0

        for i in this.game.players:
            if i.team != this.team:
                if (this.x > point.x and point.x <= i.x <= this.x) or (this.x <= point.x and this.x <= i.x <= point.x):
                    dist = abs((a * i.x + b * i.y + c) / d)
                    if dist < min:
                        min = dist
        return min
