#_*_ coding:utf-8 _*_

from handlers import weibo, weixin, zhihu, index

urls=[
    (r"/", index.MainHandler),
    (r"/weibo", weibo.WeiboHandler),
    (r"/weixin", weixin.WeixinHandler),
    (r"/zhihu", zhihu.ZhihuHandler),
]
