import os
import tornado.ioloop
import tornado.web
import memcache
import sys
reload( sys )
sys.setdefaultencoding('utf-8')

from jinja2_tornado import JinjaLoader
from urls import urls

IP = os.environ['OPENSHIFT_DIY_IP']

class Application(tornado.web.Application):
    def __init__(self, **kwargs):
        self.mc = memcache.Client(['%s:15211' % IP])
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
    port = int(os.environ['OPENSHIFT_DIY_PORT'])
    application.listen(port, IP)
    tornado.ioloop.IOLoop.instance().start()
