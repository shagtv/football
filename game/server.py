#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
from application import application

PORT = '8000'
if __name__ == "__main__":
    application.listen(PORT)
    print('Server is running http://localhost:%s/' % PORT)
    tornado.ioloop.IOLoop.instance().start()
