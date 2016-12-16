#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.render('index.html')
