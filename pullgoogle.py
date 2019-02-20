import MySQLdb
import MySQLdb.cursors
import requests
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time


global browser
browser = webdriver.Chrome()

url='https://www.google.com.hk/search?q=Luxury+Tea+sets&start=0&dpr=1'
browser.get(url)
elem = browser.find_element_by_tag_name("html")
js = 'window.scrollTo(0, document.body.scrollHeight);'
browser.execute_script(js)
time.sleep(1.5)
html = elem.get_attribute('innerHTML')
soup = BeautifulSoup(html, 'html.parser')


#广告
print('pull ad')
if soup.select("#bottomads h3"):
    for a in soup.select("#bottomads h3"):
        print(a.text)

#内容
print('pull content')
if soup.select(".g"):
    gsoup=soup.select(".g")
    for b in gsoup:

        if b.select("h3"):
            h3=b.select("h3")[0].text
            print(h3)
        if b.select("a"):
            ahref = b.select("a")[0].get("href")
            print(ahref)