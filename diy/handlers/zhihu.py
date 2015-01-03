#_*_ coding:utf-8 _*_

import tornado.web
import tornado.gen
import tornado.httpclient

import json

ZHIHU_URL = 'http://news.at.zhihu.com/api/1.2/news/latest'

headers = {
    'User-Agent':"ZhihuNotMoe/2333",
}

class ZhihuHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield client.fetch(ZHIHU_URL, headers=headers)
        if response.code == 200:
            news = json.loads(response.body.decode('utf-8'))
            entrys = news['news']
            mc = self.application.mc
            cache = mc.get('zhihu')
            if cache:
                for e in entrys:
                    if e['url'] in cache:
                        e['body'] = cache[e['url']]['body']
                        e['share_url'] = cache[e['url']]['share_url']
            no_content = [ e for e in entrys if not 'body' in e ]
            if no_content:
                responses = yield [client.fetch(x['url'], headers=headers) for x in no_content]
                for i, response in enumerate(responses):
                    if response.code == 200:
                        entry = json.loads(response.body.decode('utf-8'))
                        no_content[i]['body'] = entry['body']
                        no_content[i]['share_url'] = entry['share_url']
                    else:
                        entrys.remove(no_content[i])
                        continue
                mc.set('zhihu', dict([ (e['url'], e) for e in entrys ]), 604800)
            self.set_header("Content-Type", "application/xml; charset=UTF-8")
            self.render("zhihu.xml", entrys=entrys)
        else:
            raise tornado.web.HTTPError(response.code)
