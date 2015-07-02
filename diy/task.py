# coding: utf-8

import os, random
import memcache
import tornado.gen
import tornado.httpclient

from utils.weixin import process_cookie, process_key
from configs import WEIXIN_KEY, WEIXIN_COOKIE


IP = os.environ['OPENSHIFT_DIY_IP']

mc = memcache.Client(['%s:15211' % IP])

@tornado.gen.coroutine
def get_cookies():
    cookies = []
    client = tornado.httpclient.AsyncHTTPClient()
    for i in xrange(10):

        url = WEIXIN_COOKIE.format(q=random.choice('abcdefghijklmnopqrstuvwxyz'))

        # 获取SNUID
        request = tornado.httpclient.HTTPRequest(url=url, method='HEAD')
        response = yield client.fetch(request)
        cookie = process_cookie(response.headers['set-cookie'])

        cookies.append(cookie)

    if cookies:
        mc.set('cookie', cookies)


@tornado.gen.coroutine
def get_key():
    client = tornado.httpclient.AsyncHTTPClient()
    url = WEIXIN_KEY.format(id=random.choice('abcdefghijklmnopqrstuvwxyz'))
    response = yield client.fetch(url)
    html = response.body.decode('utf-8')
    key, level, setting = process_key(html)

    mc.set('key', (key, level, setting))
