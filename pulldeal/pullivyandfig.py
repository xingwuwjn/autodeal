import MySQLdb
import MySQLdb.cursors
import requests
import json
from bs4 import BeautifulSoup
import base64
import time
from contextlib import closing
import random
import datetime
from selenium import webdriver
import re
global browser
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument("--lang=" + "en-US")
# browser = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)
browser = webdriver.Chrome()


def tid_maker():
	return '{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now())+''.join([str(random.randint(1,10)) for i in range(5)])


#获取要爬取的url
def getData():
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql="select a.id,a.dealurl,b.deal_id from pages as a left join facebook_deal as b on a.status=0 and a.id=b.deal_id and a.name='ivyandfig' "
    urls=[]
    try:
        dealcursor=db.cursor()
        dealcursor.execute(select_sql)
        deals = dealcursor.fetchall()
        for deal in deals:
            a={}
            id=deal[0]
            url=deal[1]
            dealid=deal[2]
            if dealid is None:
                a['id']=id
                a['url']=url
                urls.append(a)

    except:
        print ("Error: unable to fecth urls")
    finally:
        dealcursor.close()
        db.close()
    return urls

#插入facebook商品详情数据
def insertDealdetatilData(result):
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    name=repr(result['name'])
    images=repr(result['images'])
    dealid=repr(result['id'])
    price = repr(result['price'])
    option=repr(result['product_option'])
    description=repr(result['description'])
    cursor = db.cursor()
    insert_sql = """
                         insert into facebook_deal(name,images,deal_id,price,option1,description)
                         VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                         name=%s,images=%s,price=%s,option1=%s,description=%s
                   """ %(name,images,dealid,price,option,description,name,images,price,option,description)
    print(insert_sql)
    try:
        cursor.execute(insert_sql)
        db.commit()
        print('insert update facebookdealdetail successed!')
        cursor.close()
    except Exception as e:
        print (e)
    db.close()



def pulldels(url):
    imgst=''
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'www.surprise.shopping',
              'Origin': 'https://www.surprise.shopping',
              'Referer': 'https://www.surprise.shopping/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    # c = requests.get(url, header)
    # html = c.content
    if 'https' not in url or 'http' not in url:
        url='https://'+url
    print("start pull url：" + url)
    browser.get(url)
    elem = browser.find_element_by_tag_name("html")
    js = 'window.scrollTo(0, document.body.scrollHeight);'
    browser.execute_script(js)
    time.sleep(1.5)
    html = elem.get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    result={}
    if soup.select(".product_name"):
       result['name']=soup.select(".product_name")[0].text
    if soup.select('.current_price .money'):
        result['price']=soup.select('.current_price .money')[0].text
    if soup.select(".flickity-slider img"):
        for img in soup.select(".product_gallery .flickity-slider img"):
            imgurl=img.get("src")
            if 'https' not in imgurl or 'http' not in imgurl:
                imgurl = 'https:' + imgurl
            if imgurl is None or imgurl=='':
                continue
            imgst=imgst+imgurl+"||"
            # print("start download url:"+'https:'+imgurl)
            # imagepath='images/'+tid_maker()+".jpg"
            # content_size=download_file('https:'+imgurl, imagepath)
            # print(content_size)
            # if content_size >0:
            #     imgst = imgst + imagepath + '||'
            # else:
            #     print('content is null')
            # print("downloaded")
        result['images']=result['images']=imgst[:-2]
    else:
        print('no images')
    if soup.select(".description"):
        description=str(soup.select(".description")[0])
        print(description)
        # description=re.sub("<[^>]*>|<\/[^>]*>/gm", "", description, 0, 0)
        result['description']=description
    if soup.select(".current_price .money"):
        result['price']=soup.select(".current_price .money")[0].text
    if soup.select(".single-option-selector option") and soup.select(".select label"):
        a={}
        color=soup.select(".select label")[0].text
        a[color]={}
        for option in soup.select(".single-option-selector option"):
            a[color][option.text]=result['price']
        result['product_option']=json.dumps(a)

    print(result)
    return result


def download_file(url, path):
    with closing(requests.get(url, stream=True)) as r:
        chunk_size = 1024 * 10
        content_size = int(r.headers['content-length'])
        if content_size <= 0:
            return content_size
        print ('下载开始')
        with open(path, "wb") as f:
            p = ProgressData(size=content_size, unit='Kb', block=chunk_size)
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                p.output()
        return content_size

class ProgressData(object):

    def __init__(self, block, size, unit, file_name='', ):
        self.file_name = file_name
        self.block = block / 1000.0    #每次下载的大小
        self.size = size / 1000.0      #文件的大小
        self.unit = unit               #下载的单位
        self.count = 0
        self.start = time.time()

    def output(self):
        self.end = time.time()
        self.count += 1
        speed = self.block / (self.end - self.start) if (self.end - self.start) > 0 else 0
        self.start = time.time()
        loaded = self.count * self.block
        progress = round(loaded / self.size, 4)
        if loaded >= self.size:
            print ('%s下载完成\r\n' % self.file_name)
        else:
            print ('{0}下载进度{1:.2f}{2}/{3:.2f}{4} 下载速度{5:.2%} {6:.2f}{7}/s'. \
                format(self.file_name, loaded, self.unit, \
                       self.size, self.unit, progress, speed, self.unit))
            print ('%50s' % ('/' * int((1 - progress) * 50)))




if __name__ == '__main__':
    urls=getData()
    for url in urls:
        result=pulldels(url['url'])
        result['id']=url['id']
        insertDealdetatilData(result)
        print("end pull url: "+url['url'])
    # url="www.ivyandfig.com/symphony"
    # result=pulldels(url)
    # insertDealdetatilData(result)