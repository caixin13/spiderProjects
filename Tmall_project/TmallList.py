from common_spider import Common_Spider
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
from pymongo import MongoClient
class TmallList(Common_Spider):

    def __init__(self):
        chorme_options=Options()
        chorme_options.add_argument("--proxy-server=http://127.0.0.1:8080")
        chorme_options.add_argument('user-agent={}'.format(self.get_random_ua()))
        prefs = {"profile.managed_default_content_settings.images": 2}
        # chorme_options.add_experimental_option("prefs", prefs)
        # chorme_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36')
        self.driver = webdriver.Chrome(chrome_options=chorme_options)
        self.login_url = 'https://login.tmall.com/'
        #此处配置淘宝账号密码
        self.user_name = 'cp水清寒'
        self.password = '.cxacp14'
        #爬取总页数为10页
        self.page = 1
        self.is_crawled = False
        #爬取列表页
        # self.url = 'https://kangaiduo.tmall.com/category-396780312.htm?spm=a1z10.15-b-s.w4011-14942273024.3.402cedf56DtBP2&search=y#TmshopSrchNav'
        self.url = 'https://kangaiduo.tmall.com/category-1136139787-1305639299.htm?spm=a1z10.15-b-s.w4011-14942273024.99.50b2edf5sv2dcj&catId=1136139787&search=y&orderType=hotsell_desc'
        self.list_url = []
        self.list_num = 0
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

    def get_url_from_list(self,url):
        self.driver.get(url)
        list_item = []
        time.sleep(2)
        divs = self.driver.find_elements_by_xpath('//div[@class="J_TItems"]/div')
        divs = divs[:-4] if len(divs) > 4 else None
        dls = []
        for div in divs:
            dl_s = div.find_elements_by_xpath('./dl')
            if len(dl_s) != 0:
               dls += dl_s
        if len(dls) != 0:
            for dl in dls:
                item = {}

                price = dl.find_elements_by_xpath(".//span[@class='c-price']")
                # print('price => {}'.format(price))
                item['价格'] = price[0].text if len(price) != 0 else None

                pro_descrip = dl.find_elements_by_xpath(".//dd[@class='detail']/a")
                item['商品描述'] = pro_descrip[0].text if len(pro_descrip) != 0 else None

                sales_num = dl.find_elements_by_xpath(".//span[@class='sale-num']")
                item['总销量'] = sales_num[0].text if len(sales_num) != 0 else None

                comment_num = dl.find_elements_by_xpath(".//h4/a/span")
                item['评价数量'] = comment_num[0].text.split(": ")[1] if len(comment_num) != 0 else None

                detail_url = dl.find_elements_by_xpath("./dt/a")
                item['详情页URL'] = detail_url[0].get_attribute('href') if len(detail_url) != 0 else None
                # print('detail_url => {}'.format(detail_url))

                self.list_url.append(item)
                print(item)
        if len(self.list_url) >= 500:
            return
        next_page = self.driver.find_elements_by_xpath('//a[@class="J_SearchAsync next"]')
        next_page = next_page[0].get_attribute('href') if len(next_page) != 0 else None
        if next_page:
            self.page += 1
            print('开始爬取页数=>{},已爬取item=>{}个'.format(self.page,len(self.list_url)))
            self.get_url_from_list(next_page)
            time.sleep(2)


    def parse_detail_url(self):
        client = MongoClient('localhost', 27017)
        db = client['tmall']['kad_otc']
        rst = db.find({},{"_id":0})
        for i in rst:
            self.driver(i['详情页URL'])
            time.sleep(2)
            
    def run(self):
        # self.login()
        # time.sleep(2)
        # self.get_url_from_list(self.url)
        # self.save_data_by_mongodb(self.list_url,'tmall','kad_rx')
        self.parse_detail_url()
if __name__ == '__main__':
    tmall = TmallList()
    tmall.run()