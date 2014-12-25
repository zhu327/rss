#_*_ coding:utf-8 _*_

from handlers import weibo, weixin, zhihu

urls=[
    #(r"/", MainHandler),
    (r"/weibo", weibo.WeiboHandler),
    (r"/weixin", weixin.WeixinHandler),
    (r"/zhihu", zhihu.ZhihuHandler),
]
