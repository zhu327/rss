# coding:utf-8

import tornado.web

from configs import ZHIHU_EXPIRES, WEIXIN_EXPIRES


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.mc = self.application.mc

    def render(self, template_name, **kwargs):
        """Renders the template with the given arguments as the response."""
        html = self.render_string(template_name, **kwargs)

        # Insert the additional JS and CSS added by the modules on the page
        js_embed = []
        js_files = []
        css_embed = []
        css_files = []
        html_heads = []
        html_bodies = []
        for module in getattr(self, "_active_modules", {}).values():
            embed_part = module.embedded_javascript()
            if embed_part:
                js_embed.append(utf8(embed_part))
            file_part = module.javascript_files()
            if file_part:
                if isinstance(file_part, (unicode_type, bytes)):
                    js_files.append(file_part)
                else:
                    js_files.extend(file_part)
            embed_part = module.embedded_css()
            if embed_part:
                css_embed.append(utf8(embed_part))
            file_part = module.css_files()
            if file_part:
                if isinstance(file_part, (unicode_type, bytes)):
                    css_files.append(file_part)
                else:
                    css_files.extend(file_part)
            head_part = module.html_head()
            if head_part:
                html_heads.append(utf8(head_part))
            body_part = module.html_body()
            if body_part:
                html_bodies.append(utf8(body_part))

        def is_absolute(path):
            return any(path.startswith(x) for x in ["/", "http:", "https:"])
        if js_files:
            # Maintain order of JavaScript files given by modules
            paths = []
            unique_paths = set()
            for path in js_files:
                if not is_absolute(path):
                    path = self.static_url(path)
                if path not in unique_paths:
                    paths.append(path)
                    unique_paths.add(path)
            js = ''.join('<script src="' + escape.xhtml_escape(p) +
                         '" type="text/javascript"></script>'
                         for p in paths)
            sloc = html.rindex(b'</body>')
            html = html[:sloc] + utf8(js) + b'\n' + html[sloc:]
        if js_embed:
            js = b'<script type="text/javascript">\n//<![CDATA[\n' + \
                b'\n'.join(js_embed) + b'\n//]]>\n</script>'
            sloc = html.rindex(b'</body>')
            html = html[:sloc] + js + b'\n' + html[sloc:]
        if css_files:
            paths = []
            unique_paths = set()
            for path in css_files:
                if not is_absolute(path):
                    path = self.static_url(path)
                if path not in unique_paths:
                    paths.append(path)
                    unique_paths.add(path)
            css = ''.join('<link href="' + escape.xhtml_escape(p) + '" '
                          'type="text/css" rel="stylesheet"/>'
                          for p in paths)
            hloc = html.index(b'</head>')
            html = html[:hloc] + utf8(css) + b'\n' + html[hloc:]
        if css_embed:
            css = b'<style type="text/css">\n' + b'\n'.join(css_embed) + \
                b'\n</style>'
            hloc = html.index(b'</head>')
            html = html[:hloc] + css + b'\n' + html[hloc:]
        if html_heads:
            hloc = html.index(b'</head>')
            html = html[:hloc] + b''.join(html_heads) + b'\n' + html[hloc:]
        if html_bodies:
            hloc = html.index(b'</body>')
            html = html[:hloc] + b''.join(html_bodies) + b'\n' + html[hloc:]

        self.mc.set(self.key, html, self.expires) # 缓存渲染的最终结果

        self.finish(html)


class ZhihuBaseHandler(BaseHandler):

    def initialize(self):
        super(ZhihuBaseHandler, self).initialize()
        self.key = 'zhihu'
        self.expires = ZHIHU_EXPIRES

    def prepare(self):
        '''
        预处理从缓存中获取html,如果能拿到,直接返回
        缓存的结果都有过期时间,过期后则再次爬去最新的内容
        知乎日报缓存3小时,微信公众号缓存1天
        '''
        html = self.mc.get(self.key)
        if html:
            self.set_header("Content-Type", "application/rss+xml; charset=UTF-8")
            self.finish(html)


class WeixinBaseHandler(BaseHandler):

    def initialize(self):
        super(WeixinBaseHandler, self).initialize()
        self.expires = WEIXIN_EXPIRES

    def prepare(self):
        self.key = str(self.get_argument('openid', ''))
        if self.key and len(self.key) == 28:
            html = self.mc.get(self.key)
            if html:
                self.set_header("Content-Type", "application/rss+xml; charset=UTF-8")
                self.finish(html)
        else:
            self.redirect("/")