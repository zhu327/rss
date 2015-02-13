#_*_ coding:utf-8 _*_

import tornado.web
import tornado.gen
import tornado.httpclient

import urllib, json, datetime, re, random, time
import lxml.html

from dateutil import tz
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
            mc = self.application.mc
            url = WINXIN_URL + urllib.urlencode({"openid": openid})
            client = tornado.httpclient.AsyncHTTPClient()

            cookies = mc.get('cookie') # 从缓存中获取cookie
            headers = random.choice(cookies)

            # 通过SUID，SUV获取接口数据
            http_request = tornado.httpclient.HTTPRequest(url=url, headers=headers)
            response = yield client.fetch(http_request)
            if response.code == 200:
                cache = mc.get(url)
                entrys = []
                content = response.body.decode('utf-8')
                content = content[content.find('{'):content.rfind('}')+1]

                content = json.loads(content)
                title = None
                title_pattern = re.compile(ur'<title><!\[CDATA\[(.+?)\]\]></title>')
                url_pattern = re.compile(ur'<url><!\[CDATA\[(.+?)\]\]></url>')
                created_pattern = re.compile(ur'<lastModified>(\d+)</lastModified>')
                for e in content['items']:
                    entry = {}
                    if not title:
                        title = re.findall(ur'<sourcename><!\[CDATA\[(.+?)\]\]></sourcename>', e)[0]
                    entry['title'] = title_pattern.findall(e)[0]
                    entry['url'] = url_pattern.findall(e)[0]
                    entry['created'] = rssdate(float(created_pattern.findall(e)[0]))
                    entrys.append(entry)
                if cache:
                    for entry in entrys:
                        if entry['url'] in cache:
                            entry['content'] = cache[entry['url']]
                no_content = [ e for e in entrys if not 'content' in e ]
                if no_content:
                    responses = yield [client.fetch(x['url']) for x in no_content]
                    for i, response in enumerate(responses):
                        if response.code == 200:
                            root = lxml.html.fromstring(response.body.decode('utf-8'))
                            cover = root.xpath('//div[@class="rich_media_thumb"]/script')
                            coverimg = None
                            if cover:
                                pic = re.findall(r'var cover = "(http://.+)";', cover[0].text)
                                if pic:
                                    coverimg = pic[0]
                            try:
                                content = root.xpath('//div[@id="js_content"]')[0]
                            except IndexError:
                                entrys.remove(no_content[i])
                                continue
                            for img in content.xpath('.//img'):
                                imgattr = img.attrib
                                imgattr['src'] = imgattr['data-src']
                            if coverimg:
                                coverelement = lxml.etree.Element('img')
                                coverelement.set('src', coverimg)
                                content.insert(0, coverelement)
                            no_content[i]['content'] = lxml.html.tostring(content, encoding='unicode')
                        else:
                            entrys.remove(no_content[i])
                            continue
                    mc.set(url, dict([ (e['url'], e['content']) for e in entrys if 'content' in e ]), 604800)
                self.set_header("Content-Type", "application/xml; charset=UTF-8")
                self.render("weixin.xml", url=url.replace('gzhjs', 'gzh'), title=title, entrys=entrys)
            else:
                raise tornado.web.HTTPError(response.code)
        else:
            self.redirect("/")
