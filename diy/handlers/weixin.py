# coding:utf-8

import time, urllib
import tornado.web
import tornado.gen
import tornado.httpclient

from base import WeixinBaseHandler
from utils.weixin import process_cookie, process_title, process_eqs, process_jsonp, process_content
from configs import SOGOU_URL, WEIXIN_URL


class WeixinHandler(WeixinBaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        id = self.key
        link = SOGOU_URL.format(id=id)
        
        # 访问搜狗的公众号页面,获取标题,构造api url
        response = yield client.fetch(link)
        
        if not response.code == 200:
            self.redirect("/")

        head = process_cookie(response.headers['set-cookie']) # 生成访问api需要的cookie
        html = response.body.decode('utf-8')
        eqs, ekv = process_eqs(html) # 生成构造api url的加密信息
        title, description = process_title(html)

        url = WEIXIN_URL.format(id=id, eqs=urllib.quote(eqs), ekv=ekv, t=int(time.time()*1000)) # 生成api url

        # 访问api url,获取公众号文章列表
        request = tornado.httpclient.HTTPRequest(url=url, headers=head)
        response = yield client.fetch(request)

        if not response.code == 200:
            self.redirect("/")

        jsonp = response.body.decode('utf-8')
        items = process_jsonp(jsonp) # 解析文章列表

        # 爬取每篇文章的内容
        responses = yield [client.fetch(i['link']) for i in items]
        for i, response in enumerate(responses):
            if response.code == 200:
                html = response.body.decode('utf-8')
                content = process_content(html)
                if content:
                    items[i]['content'] = content
                else:
                    items.pop(i)
            else:
                items.pop(i)

        pubdate = items[0]['created']

        self.set_header("Content-Type", "application/rss+xml; charset=UTF-8")
        self.render("rss.xml", title=title, description=description, items=items, pubdate=pubdate, link=link)
