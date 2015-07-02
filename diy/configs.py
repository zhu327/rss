# coding:utf-8

WEIBO_URL = 'http://service.weibo.com/widget/widget_blog.php?uid={uid}'
WEIBO_LINK = 'http://weibo.com/u/{uid}'

ZHIHU_URL = 'http://news.at.zhihu.com/api/1.2/news/latest'
ZHIHU_HEAD = {'User-Agent':"ZhihuNotMoe/2333",}

WEIXIN_KEY = 'http://weixin.sogou.com/gzh?openid={id}'
WEIXIN_COOKIE = 'http://weixin.sogou.com/weixin?query={q}'
WEIXIN_URL = 'http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid={id}&eqs={eqs}&ekv={ekv}&page=1&t={t}'

ZHIHU_EXPIRES = 3*60*60 # 知乎日报缓存3小时
WEIXIN_EXPIRES = 24*60*60 # 微信公众号缓存1天