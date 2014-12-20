import os
import tornado.ioloop
import tornado.web

from urls import urls

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

application = tornado.web.Application(
    handlers=[
        (r"/", MainHandler),
    ] + urls,
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    debug=True)

if __name__ == "__main__":
    ip = os.environ['OPENSHIFT_DIY_IP']
    port = int(os.environ['OPENSHIFT_DIY_PORT'])
    application.listen(port, ip)
    tornado.ioloop.IOLoop.instance().start()
