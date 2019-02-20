# coding: utf-8
import base64
import re
import linecache
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import MySQLdb
import MySQLdb.cursors
import memcache
import requests
from contextlib import closing
import hashlib

global browser



def fblogo():
    print('start login fb')
    count = len(open('fb.txt', 'rU').readlines())
    fbnum = random.randrange(1, count + 1, 1)  #生成随机行数
    fbaccount = linecache.getline('fb.txt', fbnum)  #随机读取某行
    fbaccount = fbaccount.replace('\r', '').replace('\n', '').replace('\t', '')
    fbaccount = fbaccount.split('|')
    fbuser = fbaccount[0]
    fbpassword = fbaccount[1]
    browser.get('https://www.facebook.com/login/')
    user = browser.find_element_by_name("email")
    user.clear()
    user.send_keys(fbuser)  #输入账号
    password = browser.find_element_by_name("pass")
    password.send_keys(fbpassword)  #输入密码
    password.send_keys(Keys.RETURN)  #实现自动点击登陆
    try:
        WebDriverWait(browser, 20, 1).until(
            EC.presence_of_element_located((By.ID, "userNavigationLabel")))
        print('logined success')
        return 1
    except:
        browser.delete_all_cookies()
        print('login error')
        time.sleep(60*5)
        fblogo()


def judgefacebooksite(url):

    browser.get(url)
    time.sleep(5)
    # 获取网页内容
    elem = browser.find_element_by_tag_name("html")
    # js = 'window.scrollTo(0, document.body.scrollHeight);'
    # for i in range(2):
    #     print('crawl' + str(i) + 'page')
    #     browser.execute_script(js)
    #     time.sleep(1.5)
    html = elem.get_attribute('innerHTML')
    # print(html)
    # 获取相关信息
    soup = BeautifulSoup(html, 'html.parser')
    if soup.select("h2[class='uiHeaderTitle']"):
        print("error")
    else:
        print("ok")


if __name__ == '__main__':
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--lang=" + "en-US")
    # browser = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
    browser = webdriver.Chrome()
    fblogo()
    urls=['https://www.facebook.com/Busysickcom-1157299861106667',
          'https://www.facebook.com/Arvitraintrysky-572810269797870',
          'https://www.facebook.com/Nicenondaya-2187608888126226/?modal=admin_todo_tour',
          'https://business.facebook.com/Beautifulworldofyou-2166034353710818/?business_id=783951228604719']
    for url in urls:
        judgefacebooksite(url)