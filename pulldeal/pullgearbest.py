#!/usr/bin/python
# -*- coding: UTF-8 -*-
from selenium import webdriver
from pulldeal.pullcontext.PullDeal import PullDeal as parent
import time
from bs4 import BeautifulSoup
import re
import base64
import json



global browser


# browser = webdriver.Chrome()
#获取gearbest详情页
class pullgearbest(parent):
    def __init__(self,url):
        self.url = url

    def formatdeal(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--lang=" + "en-US")
        browser = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)

        if 'https' not in self.url and 'http' not in self.url:
            self.url = 'https://' + self.url
        url=self.url
        print("start pull url：" + url)
        browser.get(url)
        time.sleep(5)
        elem = browser.find_element_by_tag_name("html")
        html = elem.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        #获取产品名称
        if soup.select(".goodsIntro_title"):
            result['name']=soup.select(".goodsIntro_title")[0].text
        #获取价格
        if soup.select("#js-goodsPromoPrice .goodsIntro_price"):
            result['price']=soup.select("#js-goodsPromoPrice .goodsIntro_price")[0].get("data-currency")
        #获取图片
        imgst=''
        if soup.select("#js-goodsThumbnail .slick-track .slick-slide img"):
            images=soup.select("#js-goodsThumbnail .slick-track .slick-slide img")
            for image in images:
                imagesrc=image.get("src")
                nurl = re.sub("goods_thumb-v[0-9]", "source-img", imagesrc)
                imgst=imgst+nurl+"||"
            result['images'] = result['images'] = imgst[:-2]
        #获取描述
        if soup.select("#anchorGoodsDesc"):
            description=soup.select("#anchorGoodsDesc")[0]
            description=str(description)
            # print(description)
            cc = description.replace("src", "data-cc")
            abc = cc.replace("data-lazy", "src")
            bb = abc.replace("data-cc", "data-lazy")
            # print(bb)
            # print(str(base64.b64encode(bb.encode(encoding='utf-8')), encoding='utf-8'))
            result['description']=str(base64.b64encode(bb.encode(encoding='utf-8')), encoding='utf-8')
        #获取变种
        a={}
        if soup.select(".goodsIntro_attrItem .js-goodsIntroAttr"):
            for item in soup.select(".goodsIntro_attrItem .js-goodsIntroAttr"):
                label=BeautifulSoup(str(item.find_previous_sibling("label")),"html.parser")
                label=label.string.replace(":","")
                a[label]={}
                for ahtml in item.select("a"):
                    a[label][ahtml.get("data-attr")]=result['price']
            result['product_option'] = json.dumps(a)
        try:
            browser.close()
            print("browser is closed")
        except Exception as  e:
            print(e)
        return result