#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from datetime import datetime


class Game(object):
    def __init__(self):
        self.id = random.randrange(1000)
        self.dt = datetime.now().isoformat(sep=' ')[:-7]
