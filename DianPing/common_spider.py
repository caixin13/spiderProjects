import time

from fake_useragent import UserAgent
from retrying import retry
import requests
from lxml import etree
from pymongo import MongoClient

#通用爬虫功能
class Common_Spider(object):

    #获取随机UA头的接口
    @staticmethod
    def get_random_ua():
        ua = UserAgent()
        agent = ua.random
        return agent


    #发起一个网络请求,使用retry模块，如果请求失败报错就重新发出请求
    @retry
    def make_a_request(self, url, data_type,waiting_time=0,is_proxy_pool=False):
    
        headers = {
            'User-Agent': self.get_random_ua(),
            'Referer':'http://www.dianping.com/guangzhou/ch85/g235',
            # 'Cookie':'_lxsdk_cuid=169fae07440c8-085074ba2ec85c-3c604504-1fa400-169fae07440c8; _lxsdk=169fae07440c8-085074ba2ec85c-3c604504-1fa400-169fae07440c8; _hc.v=bd91c4b0-1aa4-06e6-b09a-3e3e041530eb.1554692212; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; s_ViewType=10; cy=1500; cye=boluo; _lxsdk_s=169fb8682aa-300-0c8-cdb%7C%7C843'
            }
        #使用代理池时访问flask接口
        time.sleep(waiting_time)
        #是否使用ip池,需要先提前启动ip池
        if is_proxy_pool:
            proxy_url = 'http://0.0.0.0:5555/random'
            rst = requests.get(proxy_url)
            proxy = rst.text
            ip = {
                'http': proxy,
                'https': proxy
            }

            rst = requests.get(url, headers=headers, proxies=ip, timeout=3)
        else:
            # targetUrl = "http://test.abuyun.com"
            # targetUrl = "http://proxy.abuyun.com/switch-ip"
            # targetUrl = "http://proxy.abuyun.com/current-ip"

            # 代理服务器
            proxyHost = "http-dyn.abuyun.com"
            proxyPort = "9020"

            # 代理隧道验证信息
            proxyUser = "HDVPA67NY314087D"
            proxyPass = "55DEA9FC8386E5D8"

            proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
                "host": proxyHost,
                "port": proxyPort,
                "user": proxyUser,
                "pass": proxyPass,
            }

            proxies = {
                "http": proxyMeta,
                "https": proxyMeta,
            }
            rst = requests.get(url,headers=headers,proxies=proxies,timeout=0.5)

            # print(rst.status_code)
        #根据数据类型返回数值
        if data_type == 'text':
            return rst.text
        elif data_type == 'content':
            return rst.content.decode()
        elif data_type == 'bytes':
            return rst.content
        else:
            raise Exception('plz enter specified type')
    
    #获得结构化Html数据
    def get_html_from_data(self,data):
        if isinstance(data,str) or isinstance(data,bytes):
            html = etree.HTML(data)
            return html
        else:
            raise Exception('数据类型应为str或bytes')
    
    #使用xpath定位元素
    def get_data_by_xpath(self,html,locating_syntax,is_single=True):
        rst = html.xpath(locating_syntax)
        #返回列表还是单个数据
        if is_single:
            return rst[0] if len(rst) != 0 else '/'
        else:
            return rst
    
    #使用mongodb储存数据
    def save_data_by_mongodb(self,data,db_name,collection_name):
        client = MongoClient('localhost',27017)
        db = client[db_name][collection_name]
        if isinstance(data,list):
            for i in data:
                db.insert(i)
            print('插入数据成功')
        elif isinstance(data,dict):
            db.insert(data)
            print('插入数据成功')
        else:
            raise Exception('数据类型应为list或str')