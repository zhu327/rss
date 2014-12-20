#_*_ coding:utf-8 _*_

import tornado.web
import tornado.httpclient

import urllib, datetime, re

from bs4 import BeautifulSoup
from public import LocalTimezone, getNow

WEIBO_URL = 'http://service.weibo.com/widget/widget_blog.php?'

def rssdate(s):
    now = getNow()
    m = re.match(ur'(\d{1,2})月(\d{1,2})日 (\d{2}):(\d{2})', s)
    if m:
        date = datetime.datetime(now.year, *[int(x) for x in m.groups()], tzinfo=LocalTimezone())
    else:
        m = re.match(ur'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{2}):(\d{2})', s)
        if m:
            date = datetime.datetime(*[int(x) for x in m.groups()], tzinfo=LocalTimezone())
        else:
            m = re.match(ur'今天 (\d{2}):(\d{2})', s)
            if m:
                now.replace(hour = int(m.groups()[0]))
                now.replace(minute = int(m.groups()[1]))
                date = now
            else:
                m = re.match(ur'(\d+)分钟前', s)
                if m:
                    date = now - datetime.timedelta(minutes = int(m.groups()[0]))
                else:
                    date = now
    return date.strftime("%a, %d %b %Y %H:%M:%S %z")

class WeiboHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        uid = self.get_argument('uid', None)
        if uid and uid.isdigit() and len(uid) == 10:
            self.uid = uid
            client = tornado.httpclient.AsyncHTTPClient()
            client.fetch(WEIBO_URL + urllib.urlencode({"uid": uid}), callback=self.on_response)
        else:
            self.redirect("/")

    def on_response(self, response):
        if response.code == 200:
            soup = BeautifulSoup(response.body.decode('utf-8'))
            user = soup.find('div', attrs={'class':'userNm txt_b'}).text
            statuses = []
            for t in soup.findAll('div', attrs={'class':'wgtCell_con'}):
                status = {}
                status['content'] = t.find('p', attrs={'class':'wgtCell_txt'})
                status['title'] = status['content'].text.split('\n')[0]
                status['url'] = t.find('a', attrs={'class':'link_d'}).attrs['href']
                status['created'] = rssdate(t.find('a', attrs={'class':'link_d'}).text)
                statuses.append(status)
            self.set_header("Content-Type", "application/xml; charset=UTF-8")
            self.render("weibo.xml", uid=self.uid, user=user, statuses=statuses)
        else:
            raise tornado.web.HTTPError(response.code)
