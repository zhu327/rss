# coding:utf-8

import json

import tornado.web
import tornado.gen
import tornado.httpclient
import lxml.html

from base import ZhihuBaseHandler
from utils.filters import zhihudate
from configs import ZHIHU_URL, ZHIHU_HEAD


class ZhihuHandler(ZhihuBaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield client.fetch(ZHIHU_URL, headers=ZHIHU_HEAD)
        if response.code == 200:
            d = json.loads(response.body.decode('utf-8'))
            date = d['date']
            news = d['news']
            items = []
            for i in news:
                item = {}
                item['title'] = i['title']
                item['link'] = i['share_url']
                item['created'] = zhihudate(date, i['ga_prefix'])
                item['guid'] = i['id']
                items.append(item)

            responses = yield [client.fetch(i['url'], headers=ZHIHU_HEAD) for i in news]
            for i, response in enumerate(responses):
                if response.code == 200:
                    entry = json.loads(response.body.decode('utf-8'))
                    items[i]['content'] = entry['body']
                    root = lxml.html.fromstring(entry['body'])
                    try:
                        items[i]['author'] = root.xpath('//span[@class="author"]/text()')[0].rstrip(u'，')
                    except IndexError:
                        items[i]['author'] = 'zhihu'
                else:
                    items[i]['author'] = 'zhihu'
                    items[i]['content'] = ''

            title = u'知乎日报'
            description = u'在中国,资讯类移动应用的人均阅读时长是 5 分钟,而在知乎日报,这个数字是 21。以独有的方式为你提供最高质、最深度、最有收获的阅读体验。'
            pubdate = items[0]['created']
            link = 'http://daily.zhihu.com/'
            self.set_header("Content-Type", "application/xml")
            self.render("rss.xml", title=title, description=description, items=items, pubdate=pubdate, link=link)
        else:
            raise tornado.web.HTTPError(response.code)
