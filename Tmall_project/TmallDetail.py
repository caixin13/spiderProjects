import re

from pymongo import MongoClient

from common_spider import Common_Spider

class TmallDetail(Common_Spider):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['tmall']['kad_rx']
        self.total_list = []

    def parse_detail_url(self):
        rst = self.db.find({}, {"_id": 0})
        print(rst)
        for i in rst:
            content = self.make_a_request(i['详情页URL'], 'text', waiting_time=1)
            # print('开始解析')
            html = self.get_html_from_data(content)

            i["产品名称"] = self.get_data_by_xpath(html, '//li[contains(text(),"产品名称：")]/@title')
            i["产品剂型"] = self.get_data_by_xpath(html, '//li[contains(text(),"产品剂型:")]/@title')
            if i["产品剂型"]:
                i["产品剂型"] = i["产品剂型"].strip()
            i['用法'] = self.get_data_by_xpath(html, '//li[contains(text(),"用法:")]/@title')
            if i['用法']:
                i['用法'] = i['用法'].strip()
            i['类别'] = self.get_data_by_xpath(html, '//li[contains(text(),"类别:")]/@title')
            if i['类别']:
                i['类别'] = i['类别'].strip()
            i['药品分类'] = self.get_data_by_xpath(html, '//li[contains(text(),"药品分类:")]/@title')
            if i['药品分类']:
                i['药品分类'] = i['药品分类'].strip()
            i['套餐类型'] = self.get_data_by_xpath(html, '//li[contains(text(),"套餐类型:")]/@title')
            if i['套餐类型']:
                i['套餐类型'] = i['套餐类型'].strip()
                i['套餐类型'] = re.sub('\s', ",", i['套餐类型'])
            i['品牌'] = self.get_data_by_xpath(html, '//li[contains(text(),"品牌:")]/@title')
            if i['品牌']:
                i['品牌'] = i['品牌'].strip()
            i['批准文号'] = self.get_data_by_xpath(html, '//li[contains(text(),"批准文号:")]/@title')
            if i['批准文号']:
                i['批准文号'] = i['批准文号'].strip()
            i['使用剂量'] = self.get_data_by_xpath(html, '//li[contains(text(),"使用剂量:")]/@title')
            if i['使用剂量']:
                i['使用剂量'] = i['使用剂量'].strip()
            i['药品通用名'] = self.get_data_by_xpath(html, '//li[contains(text(),"药品通用名:")]/@title')
            if i['药品通用名']:
                i['药品通用名'] = i['药品通用名'].strip()

            i['药品名称'] = self.get_data_by_xpath(html, '//li[contains(text(),"药品名称:")]/@title')
            if i['药品名称']:
                i['药品名称'] = i['药品名称'].strip()
            i['规格'] = self.get_data_by_xpath(html, '//li[contains(text(),"规格:")]/@title')
            if i['规格']:
                i['规格'] = i['规格'].strip()
            i['有效期'] = self.get_data_by_xpath(html, '//li[contains(text(),"有效期:")]/@title')
            if i['有效期']:
                i['有效期'] = i['有效期'].strip()
            i['生产企业'] = self.get_data_by_xpath(html, '//li[contains(text(),"生产企业:")]/@title')
            if i['生产企业']:
                i['生产企业'] = i['生产企业'].strip()
            self.total_list.append(i)
            print(i)

    def run(self):
        self.parse_detail_url()
        self.save_data_by_mongodb(self.total_list,"tmall",'rx_info')


if __name__ == '__main__':

    tmall = TmallDetail()
    tmall.run()