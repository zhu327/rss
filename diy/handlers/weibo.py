# coding:utf-8

import tornado.web
import tornado.httpclient
import lxml.html

from utils.filters import weibodate
from configs import WEIBO_URL, WEIBO_LINK


class WeiboHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        uid = self.get_argument('uid', None)
        if uid and uid.isdigit() and len(uid) == 10:
            self.uid = uid
            client = tornado.httpclient.AsyncHTTPClient()
            client.fetch(WEIBO_URL.format(uid=uid), callback=self.on_response)
        else:
            self.redirect("/")

    def on_response(self, response):
        if response.code == 200:
            root = lxml.html.fromstring(response.body.decode('utf-8'))
            author = root.xpath('//*[@id="widget_wapper"]/div/div[1]/div[2]/div[1]/text()')[0]
            title = u'{author}的微博'.format(author=author)
            items = []
            for t in root.xpath('//*[@id="content_all"]/*/div[@class="wgtCell_con"]'):
                item = {}
                content = t.xpath('p[@class="wgtCell_txt"]')[0]
                item['content'] = lxml.html.tostring(content, encoding='unicode')
                item['title'] = content.text_content().split('\n')[0]
                link = t.xpath('div/span[@class="wgtCell_tm"]/a')[0]
                item['link'] = link.get('href')
                item['created'] = weibodate(link.text)
                item['guid'] = item['link']
                item['author'] = author
                items.append(item)
            pubdate = items[0]['created']
            link = WEIBO_LINK.format(uid=self.uid)
            self.set_header("Content-Type", "application/xml")
            self.render("rss.xml", title=title, description=title, items=items, pubdate=pubdate, link=link)
        else:
            raise tornado.web.HTTPError(response.code)
