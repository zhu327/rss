### RSS Factory

***

demo:<https://diy-devz.rhcloud.com>

RSS Factory 是用于生成 微博 微信公众号 知乎日报 RSS 的Web APP.  

demo服务搭建在OpenShift上，搭建步骤参考以下链接：  
1. 搭建OpenShift Tornado DIY环境  
> <http://bozpy.sinaapp.com/blog/29>
2. 在OpenShift上安装memcached  
> <http://www.blackglory.me/openshift-install-wordpress-memcached/>
```shell
# 启动memcached  
$OPENSHIFT_DATA_DIR/bin/memcached -l $OPENSHIFT_DIY_IP -p 15211 -d  
# 获取pid用于停止服务  
ps -ef|grep memcached
```
3. 安装Python依赖库
```shell
pip install -r requirements.txt
```
4. git push RSS Factory的代码

为了便于小伙伴们搭建自己的微信公众号RSS，提供Docker image一键构建，只需要注册灵雀云就好。  
image: <https://hub.alauda.cn/repos/zhu327/rss>


注意：
由于搜狗微信公众号搜索强大的反爬虫机制，demo服务在公众号订阅超过300订阅后就会500，所以如果你需要公众号RSS服务的话请自己用上面提供的Docker镜像自己搭建。
