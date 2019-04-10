from queue import Queue

from pymongo import MongoClient

from common_spider import Common_Spider
from threading import Thread
import datetime


class DianPing(Common_Spider):

    def __init__(self):
   
        self.page = 1
        self.item_list = []

    def parse_list_url(self,url):

        item_list = []
        print('开始爬取第{}页'.format(self.page))
        rst = self.make_a_request(url,"content",waiting_time=2)

        html = self.get_html_from_data(rst)
        lis = self.get_data_by_xpath(html,'//div[@id="shop-all-list"]/ul/li',is_single=False)
        if len(lis):
            for li in lis:
                item = {}
                is_divided = self.get_data_by_xpath(li,'.//a[@class="shop-branch"]/text()')
                item['是否分店'] = '是' if '/'not in is_divided else '否'
                item['详情页'] = self.get_data_by_xpath(li,'./div[2]/div[1]/a[1]/@href')
                item_list.append(item)
                print(item)
            self.save_data_by_mongodb(item_list,'dianping','dp_detail_url')
        else:
            print('error')


        next_url = self.get_data_by_xpath(html,'//a[contains(text(),"下一页")]/@href')
        if next_url != '/':
            self.page += 1
            self.parse_list_url(next_url)
        else:
            print('已爬取{}页'.format(self.page))

    def parse_detail_url(self,item):
        rst = self.make_a_request(item['详情页'],'content')
        # print(rst)
        html = self.get_html_from_data(rst)
        if not html:
            self.parse_detail_url(item)
            print('重试')
            return
       
        item['店名'] = self.get_data_by_xpath(html, '//*[@id="basic-info"]/h1/text()')
        if item['店名'] == '/':
            print('重试')
            self.parse_detail_url(item)
            return
        item["城市"] = self.get_data_by_xpath(html,'//a[@class="city J-city"]/span[2]/text()')
        item['区域'] = self.get_data_by_xpath(html,'//div[@class="breadcrumb"]/a[3]/text()')
        item['地址'] = self.get_data_by_xpath(html,'//span[@itemprop="street-address"]/text()')
        item['联系方式'] = self.get_data_by_xpath(html,'//p[@class="expand-info tel"]/span[2]/text()')

        item["营业时间"] = self.get_data_by_xpath(html,'//p[@class="info info-indent"]/span[2]/text()')

        item['人均消费'] = self.get_data_by_xpath(html,'//span[@id="avgPriceTitle"]/text()')
        if ':' in item['人均消费']:
            item['人均消费'] = item['人均消费'].split(':')[1]
        item['评论数'] = self.get_data_by_xpath(html,'//span[@id="reviewCount"]/text()')
        item['总分'] = self.get_data_by_xpath(html,'//div[@class="brief-info"]/span[1]/@class')
        # print(item)
        if item['总分'] != '/':
            score = item['总分'].split("str")[1]
            if len(score) == 1:
                final_score = 0.0
            else:
                final_score = score[0] + '.' + score[1]
            item['总分'] = final_score
        print(item)
        self.item_list.append(item)


    def save_urls(self,urls):

        with open('{}_urls.txt'.format(self.city),'a') as f:
            for url in urls:
                print(url)
                f.write(url)
                f.write('\n')

    def run(self):
        pastTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 现在
        print('开始时间=>{}'.format(pastTime))
        client = MongoClient('localhost', 27017)
        db = client['dianping']['dp_detail_url']
        rst = db.find({}, {'_id': 0})
        for i in rst[:10000]:

            self.parse_detail_url(i)
            if len(self.item_list) == 500:
                self.save_data_by_mongodb(self.item_list, 'dianping', 'final_item')
                self.item_list = []
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 现在
        print('{}=>{}结束'.format(pastTime,nowTime))


if __name__ == '__main__':
    dianping = DianPing()
    dianping.run()
