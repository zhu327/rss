#_*_ coding:utf-8 _*_

import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
