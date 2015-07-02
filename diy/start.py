import os, sys

_basedir = os.path.abspath(os.path.dirname(__file__))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

reload( sys )
sys.setdefaultencoding('utf-8')

import memcache
import tornado.ioloop
import tornado.web

from jinja2_tornado import JinjaLoader
from urls import urls
from task import get_cookies, get_key

IP = os.environ['OPENSHIFT_DIY_IP']
PORT = int(os.environ['OPENSHIFT_DIY_PORT'])

mc = memcache.Client(['%s:15211' % IP])

class Application(tornado.web.Application):
    def __init__(self, **kwargs):
        self.mc = mc
        super(Application, self).__init__(**kwargs)


application = Application(
    handlers=urls,
    static_path=os.path.join(_basedir, "static"),
    template_loader=JinjaLoader(os.path.join(_basedir, 'templates'),
        autoescape=True, extensions=['jinja2.ext.autoescape']),
    debug = True,
)

if __name__ == "__main__":
    application.listen(PORT, IP)
    tornado.ioloop.PeriodicCallback(get_cookies, 24*60*60*1000).start()
    tornado.ioloop.PeriodicCallback(get_key, 15*60*60*1000).start()
    tornado.ioloop.IOLoop.instance().start()
