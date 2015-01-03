import os
import tornado.ioloop
import tornado.web
import memcache

from jinja2_tornado import JinjaLoader
from urls import urls

LOCAL_IP = os.environ['OPENSHIFT_DIY_IP']

class Application(tornado.web.Application):
    def __init__(self, **kwargs):
        self.mc = memcache.Client(['%s:15211' % LOCAL_IP])
        tornado.web.Application.__init__(self, **kwargs)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

urls.append((r"/", MainHandler))

application = Application(
    handlers=urls,
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    template_loader=JinjaLoader(os.path.join(os.path.dirname(__file__), 'templates/'),
        autoescape=True, extensions=['jinja2.ext.autoescape']),
)

if __name__ == "__main__":
    ip = os.environ['OPENSHIFT_DIY_IP']
    port = int(os.environ['OPENSHIFT_DIY_PORT'])
    application.listen(port, ip)
    tornado.ioloop.IOLoop.instance().start()
