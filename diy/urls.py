# coding:utf-8

from handlers import weibo, weixin, zhihu, index

urls=[
    (r"/", index.MainHandler),
    (r"/weibo", weibo.WeiboHandler),
    (r"/gzh", weixin.WeixinHandler),
    (r"/zhihu", zhihu.ZhihuHandler),
]
