# coding: utf-8
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
import requests
import json
global browser


#获取要检测的url
def getData():

    #获取还未爬取的页面url
    select_sql="""select id,text,phone from cmf_listen where is_listen=1
                """
    urlsarray=[]
    try:
        urlcursor=db.cursor()
        urlcursor.execute(select_sql)
        urls = urlcursor.fetchall()
        for content in urls:
            a={}
            id=content[0]      #产品id
            url=content[1]    #url
            phone=content[2]
            if url =='' or url is None:
                continue
            a['id']=id
            a['url']=url
            a['phone'] = phone
            urlsarray.append(a)
    except:
        print ("Error: unable to fecth urls")
    finally:
        urlcursor.close()
    return urlsarray


#更新page状态
def updatestatus(status,id):
    select_sql = '''
                   update cmf_listen set status=%s where id=%s
                    '''%(status,id)
    # print(select_sql)
    try:
        cursor = db.cursor()
        cursor.execute(select_sql)
        db.commit()
        print('update status=%s,id=%s successed!'%(status,id))
    except:
        print("Error: unable to update page.sp_status=%s,id=%s"%(status,id))
    finally:
        cursor.close()



#更新page状态
def updatesis_listen(status,id):
    select_sql = '''
                   update cmf_listen set is_listen=%s where id=%s
                    '''%(status,id)
    # print(select_sql)
    try:
        cursor = db.cursor()
        cursor.execute(select_sql)
        db.commit()
        print('update is_listen=%s,id=%s successed!'%(status,id))
    except:
        print("Error: unable to update is_listen=%s,id=%s"%(status,id))
    finally:
        cursor.close()




#发送短信
def sendmsg(url,phone):
    data = {'type': 'python',
            'name': 'NGE',
            'text': url,
            'phone': phone}
    r = requests.post('http://www.onenewsiri.com/user/send_message/pythonsend.html', data=data)
    print(r.content)
    if r.status_code == 200:
        print('send msg ok')
        # print(r.text)
        # print(r.content)


#模拟登陆
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


#判断facebook粉丝页是否正常
def judgefacebooksite(url,id,phone):

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
        print('facebook_site：' + url + " is error")
        updatestatus(0,id)
        sendmsg(url, phone)
    else:
        print('facebook_site：' + url + " is ok")
        updatestatus(1, id)


#判断域名是否正常
def judgedomain(url,id,phone):
    try:
        uu=requests.get(url,timeout=5)
        if uu.status_code == 200:
            print('shopfiyurl：'+url+" is ok" )
            updatestatus(1, id)
        else:
            print('shopfiyurl：' + url + " is error")
            updatestatus(0, id)
            sendmsg(url, phone)

    except Exception as e:
        print('shopfiyurl：' + url + " is error")
        updatestatus(0, id)
        sendmsg(url, phone)

# if __name__ == '__main__':
#     # chrome_options = webdriver.ChromeOptions()
#     # chrome_options.add_argument('--headless')
#     # chrome_options.add_argument('--no-sandbox')
#     # chrome_options.add_argument('--disable-dev-shm-usage')
#     # chrome_options.add_argument("--lang=" + "en-US")
#     # browser = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
#     browser = webdriver.Chrome()
#     fblogo()
#     # urls=['https://www.facebook.com/Busysickcom-1157299861106667',
#     #       'https://www.facebook.com/Arvitraintrysky-572810269797870',
#     #       'https://www.facebook.com/Nicenondaya-2187608888126226/?modal=admin_todo_tour',
#     #       'https://business.facebook.com/Beautifulworldofyou-2166034353710818/?business_id=783951228604719']
#     db = MySQLdb.connect("52.13.162.7", "websitedb", "imagedb", "image5v2jHYD", charset='utf8')
#     urls=getData()
#     for urldict in urls:
#         url=urldict['url']
#         id=urldict['id']
#         phone=urldict['phone']
#         if 'facebook' in url:
#             judgefacebooksite(url,id,phone)
#         else:
#             judgedomain(url,id,phone)


while(True):
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--lang=" + "en-US")
    # browser = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
    browser = webdriver.Chrome()
    fblogo()
    db = MySQLdb.connect(host="52.13.162.7", user="imagedb", db="websitedb", passwd="image5v2jHYD",port=4306, charset='utf8')
    urls=getData()
    print(urls)
    for urldict in urls:
        url=urldict['url']
        id=urldict['id']
        phone=urldict['phone']

        if 'facebook' in url:
            judgefacebooksite(url,id,phone)
        else:
            judgedomain(url,id,phone)
        updatesis_listen(99, id)  #爬取过
    try:
        browser.close()
        print("browser is closed")
    except Exception as  e:
        print(e)
    time.sleep(5*60)
    print('sleeping ...')