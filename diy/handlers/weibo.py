#_*_ coding:utf-8 _*_

import tornado.web
import tornado.httpclient

import urllib, datetime, re
import lxml.html

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
            root = lxml.html.fromstring(response.body.decode('utf-8'))
            user = root.xpath("//div[@class='userNm txt_b']")[0].text
            statuses = []
            for t in root.xpath("//div[@class='wgtCell_con']"):
                status = {}
                content = t.xpath("p[@class='wgtCell_txt']")[0]
                status['content'] = lxml.html.tostring(content, encoding='unicode')
                status['title'] = content.text_content().split('\n')[0]
                time = t.xpath(".//a[@class='link_d']")[0]
                status['url'] = time.get('href')
                status['created'] = rssdate(time.text)
                statuses.append(status)
            self.set_header("Content-Type", "application/xml; charset=UTF-8")
            self.render("weibo.xml", uid=self.uid, user=user, statuses=statuses)
        else:
            raise tornado.web.HTTPError(response.code)
