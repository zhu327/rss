# coding:utf-8

import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', host=self.request.host)
