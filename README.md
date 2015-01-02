### RSS Factory

***

demo:<https://diy-devz.rhcloud.com>

RSS Factory 是用于生成 微博 微信公众号 知乎日报 RSS 的Web APP。  

部署在Openshift diy tornado环境上，环境搭建参考:  
<http://blog.ricoxie.com/2014/04/29/deploy-tornado-on-openshift-diy/>  

<del>另外还依赖BeautifulSoup</del>

模版引擎改为jinja2, html解析改为lxml

写这个APP是为了学习tornado异步请求，tornado没有用多线程实现并发，而是用事件循环来处理，所以这里主要用到了异步http client，同时fetch多个url也不会太慢
