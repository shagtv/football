#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handlers.web import MainHandler
from handlers.ws import GameHandler

urls = [
  (r'/', MainHandler),
  (r'/ws', GameHandler)
]
