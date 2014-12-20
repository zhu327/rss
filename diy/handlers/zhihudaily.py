#_*_ coding:utf-8 _*_

import tornado.web
import tornado.gen
import tornado.httpclient

import json

ZHIHU_URL = 'http://news.at.zhihu.com/api/1.2/news/latest'

headers = {
    'User-Agent':"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)",
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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
            responses = yield [client.fetch(x['url'], headers=headers) for x in entrys]
            for i, response in enumerate(responses):
                if response.code == 200:
                    entry = json.loads(response.body.decode('utf-8'))
                    entrys[i]['body'] = entry['body']
                else:
                    continue
            self.set_header("Content-Type", "application/xml; charset=UTF-8")
            self.render("zhihu.xml", entrys=entrys)
        else:
            raise tornado.web.HTTPError(response.code)
