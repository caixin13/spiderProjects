# from urllib import parse

# import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC, expected_conditions
import time
# from pyquery import PyQuery as pq
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import random
import json
# import re
# import traceback
# from lxml import etree
from common_spider import Common_Spider

class Tmall(Common_Spider):
    # 浏览器初始化
    def __init__(self):
        chorme_options=Options()
        chorme_options.add_argument("--proxy-server=http://127.0.0.1:8080")
        chorme_options.add_argument('user-agent={}'.format(self.get_random_ua()))
        prefs = {"profile.managed_default_content_settings.images": 2}
        chorme_options.add_experimental_option("prefs", prefs)
        # chorme_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36')
        self.driver=webdriver.Chrome(chrome_options=chorme_options)
        self.login_url = 'https://login.tmall.com/'
        #此处配置淘宝账号密码
        self.user_name = 'xxxx'
        self.password = 'xxxx'
        #爬取页数
        self.page = 1
        self.is_crawled = False
        #爬取列表页
        self.url = 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.0.0.7750e87dmdUJcT&cat=57056001&sort=s&style=g&search_condition=23&from=sn_1_rightnav&active=1&industryCatId=55168012&smAreaId=440100'


    # 登录
    def login(self):
        self.driver.get(self.login_url)

        iframe = self.driver.find_element_by_xpath('//*[@id="J_loginIframe"]')
        self.driver.switch_to_frame(iframe)
        
        self.driver.execute_script('document.getElementById("J_Quick2Static").click()')
        # self.driver.find_element_by_xpath('//*[@id="J_Quick2Static"]').click()
        time.sleep(1)
        # for i in '17647466350':
        for i in self.user_name:
            self.driver.find_element_by_id('TPL_username_1').send_keys(i)
            time.sleep(0.2)
        time.sleep(1)
        # for i in '2153874abcd':
        for i in self.password:
            self.driver.find_element_by_id('TPL_password_1').send_keys(i)
            time.sleep(0.2)
        time.sleep(0.5)
        self.driver.find_element_by_id('J_SubmitStatic').click()

    # 翻页处理
    # def next_page(self,ky):
    #     try:
    #         # 翻页
    #         WebDriverWait(self.driver, 6, 0.5).until(
    #             expected_conditions.visibility_of_element_located((By.PARTIAL_LINK_TEXT, '下一页')))
    #         np = self.driver.find_element_by_partial_link_text('下一页')
    #         self.driver.execute_script("arguments[0].click();", np)
    #         return True
    #     except:
    #         print('当前关键字：【{}】没有下一页了'.format(ky))
    #         return False

    def get_detail_url(self,url):
        #获取列表页中商品url
        if self.page != 1:
            url = self.url + '&s={}'.format(60*(self.page-1))
        self.driver.get(url)
        url_list = []
        # time.sleep(random.randint(5,7))
        time.sleep(2)
        detail_urls = self.driver.find_elements_by_xpath('//*[@id="J_ItemList"]/div/div/div[1]/a')
        for detail_url in detail_urls:
            url_list.append(detail_url.get_attribute('href'))
        print(len(detail_urls))
        self.parse_detail_url(url_list)

        # if self.next_page('保健与健康'):
        if self.page <= 80:
            self.page += 1
            url = self.url + '&s={}'.format(60*(self.page-1))
            print('第{}页开始爬取'.format(self.page))
            self.get_detail_url(url)


    def parse_detail_url(self,url_list):
        item_list = []
        for url in url_list:
            item = {}
            
            self.driver.get(url)
            time.sleep(random.randint(5,7))
            prices = self.driver.find_elements_by_xpath('//span[@class="tm-price"]')
            if len(prices) != 2:
                item['促销价'] = prices[0].text
            else:
                item['促销价'] = prices[1].text
            sales = self.driver.find_elements_by_xpath('//li[@data-label="月销量"]/div/span[2]')
            item['月销量'] = sales[0].text if len(sales) != 0 else None
            title = self.driver.find_elements_by_xpath('//div[@class="tb-detail-hd"]/h1')
            item['商品描述'] = title[0].text.strip() if len(title) != 0 else None
            approval_num = self.driver.find_elements_by_xpath("//li[contains(text(),'生产许可证编号')]")
            item['批准文号'] = approval_num[0].get_attribute('title') if len(approval_num) != 0 else None
            target_man = self.driver.find_elements_by_xpath("//li[contains(text(),'适用人群')]")
            item['适用人群'] = target_man[0].get_attribute('title') if len(target_man) != 0 else None
            brand = self.driver.find_elements_by_xpath("//li[contains(text(),'品牌')]")
            item['品牌'] = brand[0].get_attribute('title') if len(brand) != 0 else None
            factory_name = self.driver.find_elements_by_xpath("//li[contains(text(),'厂名')]")
            item['厂名'] = factory_name[0].get_attribute('title') if len(factory_name) != 0 else None
            factory_address = self.driver.find_elements_by_xpath("//li[contains(text(),'厂址')]")
            item['厂址'] = factory_address[0].get_attribute('title') if len(factory_address) != 0 else None
            factory_phone = self.driver.find_elements_by_xpath("//li[contains(text(),'厂家联系方式')]")
            item['厂家联系方式'] = factory_phone[0].get_attribute('title') if len(factory_phone) != 0 else None
            use_date = self.driver.find_elements_by_xpath("//li[contains(text(),'保质期')]")
            item['保质期'] = use_date[0].get_attribute('title') if len(use_date) != 0 else None
            product_formulations = self.driver.find_elements_by_xpath("//li[contains(text(),'产品剂型')]")
            item['产品剂型'] = product_formulations[0].get_attribute('title') if len(product_formulations) != 0 else None
            product_size = self.driver.find_elements_by_xpath("//li[contains(text(),'具体规格')]")
            item['具体规格'] = product_size[0].get_attribute('title') if len(product_size) != 0 else None
            storage_method = self.driver.find_elements_by_xpath("//li[contains(text(),'储藏方法')]")
            item['储藏方法'] = storage_method[0].get_attribute('title') if len(storage_method) != 0 else None
            burden_sheet = self.driver.find_elements_by_xpath("//li[contains(text(),'配料表')]")
            item['配料表'] = burden_sheet[0].get_attribute('title') if len(burden_sheet) != 0 else None
            pro_maker = self.driver.find_elements_by_xpath("//li[contains(text(),'产地')]")
            item['产地'] = pro_maker[0].get_attribute('title') if len(pro_maker) != 0 else None
            effect = self.driver.find_elements_by_xpath("//li[contains(text(),'功能')]")
            item['功能'] = effect[0].get_attribute('title') if len(effect) != 0 else None
            need_attention = self.driver.find_elements_by_xpath("//li[contains(text(),'注意事项')]")
            item['注意事项'] = need_attention[0].get_attribute('title') if len(need_attention) != 0 else None
            pro_name = self.driver.find_elements_by_xpath("//li[contains(text(),'产品名称')]")
            item['产品名称'] = pro_name[0].get_attribute('title') if len(pro_name) != 0 else None
            item['商品详情url'] = url
            print(item)
            item_list.append(item)
        self.save_item(item_list)

    def save_item(self,total_rst):
        with open('final_rst','a') as f:
            for item in total_rst:
                json.dump(item,f,ensure_ascii=False)
                f.write('\n')
        print('saved page:{} successful'.format(self.page))

    # 程序运行
    def run(self):
        self.login()
        time.sleep(4)
        self.get_detail_url(self.url)
        self.driver.quit()

        
if __name__ == '__main__':
    tmallspider = Tmall()
    tmallspider.run()

