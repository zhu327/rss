#_*_ coding:utf-8 _*_

import tornado.web
import tornado.gen
import tornado.httpclient

import urllib, json, datetime
from dateutil import tz
from bs4 import BeautifulSoup
from public import LocalTimezone

WINXIN_URL = 'http://weixin.sogou.com/gzhjs?'

def rssdate(date):
    utc = datetime.datetime.utcfromtimestamp(date)
    utc = utc.replace(tzinfo=tz.gettz('UTC'))
    local = utc.astimezone(LocalTimezone())
    return local.strftime("%a, %d %b %Y %H:%M:%S %z")

class WeixinHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        openid = self.get_argument('openid', None)
        if openid and len(openid) == 28:
            url = WINXIN_URL + urllib.urlencode({"openid": openid})
            client = tornado.httpclient.AsyncHTTPClient()
            response = yield client.fetch(url)
            if response.code == 200:
                entrys = []
                content = response.body.decode('utf-8')
                content = content[content.index('{'):content.rfind('}')+1]
                content = json.loads(content)
                title = None
                for e in content['items']:
                    soup = BeautifulSoup(e)
                    entry = {}
                    if not title:
                        title = soup.find('sourcename').text
                    entry['title'] = soup.find('title').text
                    entry['url'] = soup.find('url').text
                    entry['created'] = rssdate(float(soup.find('lastmodified').text))
                    entrys.append(entry)
                responses = yield [client.fetch(x['url']) for x in entrys]
                for i, response in enumerate(responses):
                    if response.code == 200:
                        s = BeautifulSoup(response.body.decode('utf-8'))
                        content = s.find('div', id='js_content')
                        entrys[i]['content'] = content
                    else:
                        del entrys[i]
                        continue
                self.set_header("Content-Type", "application/xml; charset=UTF-8")
                self.render("weixin.xml", url=url.replace('gzhjs', 'gzh'), title=title, entrys=entrys)
            else:
                raise tornado.web.HTTPError(response.code)
        else:
            self.redirect("/")
