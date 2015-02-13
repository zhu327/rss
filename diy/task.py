# coding: utf-8

import random, re, time, os
import memcache
import tornado.gen
import tornado.httpclient

IP = os.environ['OPENSHIFT_DIY_IP']

def getSUV():
    return '='.join(['SUV', str(int(time.time()*1000000) + random.randint(0, 1000))])

@tornado.gen.coroutine
def get_cookies():
    cookies = []
    client = tornado.httpclient.AsyncHTTPClient()
    for i in xrange(10):

        url = 'http://weixin.sogou.com/weixin?query=%s' % random.choice('abcdefghijklmnopqrstuvwxyz')

        # 获取SNUID
        cookie_request = tornado.httpclient.HTTPRequest(url=url, method='HEAD')
        cookie = yield client.fetch(cookie_request)
        SUID = re.findall(r'(SUID=\S+?);', cookie.headers['set-cookie'])[0]
        m = re.findall(r'(SNUID=\S+?);', cookie.headers['set-cookie'])
        if m:
            SNUID = m[0]
            headers = {'Cookie:': '; '.join([SUID, getSUV(), SNUID])}
            cookies.append(headers)

    mc = memcache.Client(['%s:15211' % IP])

    if cookies:
        mc.set('cookie', cookies)
