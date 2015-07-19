### RSS Factory

***

demo:<https://diy-devz.rhcloud.com> (demo不再提供微信公众号rss生成服务,有需要可以自行搭建)

RSS Factory 是用于生成 微博 微信公众号 知乎日报 RSS 的Web APP。  

<https://hub.alauda.cn/repos/zhu327/rss>  
提供Docker image用于一键构建你自己RSS服务。  

部署在Openshift diy tornado环境上，环境搭建参考:  
<http://bozpy.sinaapp.com/blog/29>

<del>另外还依赖BeautifulSoup</del>

模版引擎改为jinja2, html解析改为lxml

新增memcahed缓存，加速访问微信，知乎 rss  
Openshift安装memcached参考  
<http://www.blackglory.me/openshift-install-wordpress-memcached/>

启动memcached  
$OPENSHIFT_DATA_DIR/bin/memcached -l $OPENSHIFT_DIY_IP -p 15211 -d  
获取pid用于停止服务  
ps -ef|grep memcached  

还需要安装  
$OPENSHIFT_DATA_DIR/bin/pip install python-memcached

写这个APP是为了学习tornado异步请求，tornado没有用多线程实现并发，而是用事件循环来处理，所以这里主要用到了异步http client，同时fetch多个url也不会太慢

2015.02.05 搜狗微信公众号已启用反爬虫，我在代码中已添加针对反爬虫的措施，但是不保证一定有效，间歇性的500是不可避免的

2015.02.14 更新了定时任务，每6个小时更新一次cookie，获取10个有效cookie，微信公众号api随机使用可用cookie，基本解决搜狗反爬虫问题

2015.07.02 重构了下代码,看起来更像一个标准的项目,再次尝试解决搜狗的反爬虫问题,通过缓存来减少对文章列表的请求数,依赖在requirements.txt中

2015.07.14 微信公众号再一次500,反爬虫很厉害,大概微信公众号订阅到300的时候就不行了,所以demo不再提供微信公众号rss的生成服务,有兴趣可用自己搭建,非公开自用应该不会产生反爬虫的问题,抱歉
