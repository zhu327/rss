# coding:utf-8

import time, random, urllib
import tornado.web
import tornado.gen
import tornado.httpclient

from base import WeixinBaseHandler
from utils.weixin import process_eqs, process_jsonp, process_content
from configs import WEIXIN_KEY, WEIXIN_URL


class WeixinHandler(WeixinBaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        id = self.key
        link = WEIXIN_KEY.format(id=id)

        cookies = self.mc.get('cookie')
        head = random.choice(cookies)

        key = self.mc.get('key')
        eqs = process_eqs(key[0], id, key[2])

        url = WEIXIN_URL.format(id=id, eqs=urllib.quote(eqs), ekv=key[1], t=int(time.time()*1000)) # 生成api url

        # 访问api url,获取公众号文章列表
        request = tornado.httpclient.HTTPRequest(url=url, headers=head)
        response = yield client.fetch(request)

        if not response.code == 200:
            self.redirect("/")

        jsonp = response.body.decode('utf-8')
        items = process_jsonp(jsonp) # 解析文章列表

        if not items:
            self.set_header("Content-Type", "application/rss+xml; charset=UTF-8")
            self.render("rss.xml", title='', description='', items=items, pubdate='', link=link)

        # 爬取每篇文章的内容
        responses = yield [client.fetch(i['link']) for i in items]
        for i, response in enumerate(responses):
            if response.code == 200:
                html = response.body.decode('utf-8')
                content = process_content(html)
                items[i]['content'] = content
            else:
                items[i]['content'] = ''

        pubdate = items[0]['created']
        title = description = items[0]['author']

        self.set_header("Content-Type", "application/rss+xml; charset=UTF-8")
        self.render("rss.xml", title=title, description=description, items=items, pubdate=pubdate, link=link)
