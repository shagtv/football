#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
from application import application
from handlers.ws import GameHandler

PORT = '8000'
if __name__ == "__main__":
    application.listen(PORT)
    print('Server is running http://localhost:%s/' % PORT)

    loop = tornado.ioloop.IOLoop.instance()
    period_cbk = tornado.ioloop.PeriodicCallback(GameHandler.period_run, 50, loop)
    period_cbk.start()
    loop.start()
