# coding: utf-8
import requests
import MySQLdb
import MySQLdb.cursors
import json
import ssl
import urllib3
urllib3.disable_warnings()   #防止   verify=False 报错
from bs4 import BeautifulSoup
import time
import base64
re=requests.session()
import os
import sys
sys.path.append(os.getcwd()+'/pulldeal')

#获取要爬取的url
def getData():

    #获取还未爬取的页面url
    select_sql="""select a.id,a.dealurl,b.deal_id,a.name from pages as a left join facebook_deal as b 
                  on a.id=b.deal_id where a.sp_status=0
                """
    urls=[]
    try:
        dealcursor=db.cursor()
        dealcursor.execute(select_sql)
        deals = dealcursor.fetchall()
        for deal in deals:
            a={}
            id=deal[0]      #产品id
            url=deal[1]     #url
            dealid=deal[2]  #产品详情表id
            sitename = deal[3]  # 产品详情表id
            if url =='' or url is None:
                continue
            if dealid is None:
                a['id']=id
                a['url']=url
                a['sitename']=sitename
                urls.append(a)

    except:
        print ("Error: unable to fecth urls")
    finally:
        dealcursor.close()
    return urls



#更新page状态
def updatestatus(status,id):
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql = '''
                   update pages set sp_status=%s where id=%s
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




#插入facebook商品详情数据
def insertDealdetatilData(result):
    if result['name'] is None:
        print('data is error')
    name=repr(result['name'])
    images=repr(result['images'])
    dealid=repr(result['dealid'])
    price = repr(result['price'])
    option=repr(result['product_option'])
    description=repr(result['description'])
    insert_sql = """
                         insert into facebook_deal(name,images,deal_id,price,option1,description)
                         VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                         name=%s,images=%s,price=%s,option1=%s,description=%s
                   """ %(name,images,dealid,price,option,description,name,images,price,option,description)
    # print(insert_sql)
    try:
        cursor = db.cursor()
        cursor.execute(insert_sql)
        db.commit()
        print('insert update facebookdealdetail successed!')
    except Exception as e:
        print (e)
    finally:
        cursor.close()



#依据短链接获取长链接
def revertShortLink(url):
    try:
        res = requests.head(url)
        location=res.headers.get('location')
        if location is None:
            return url
    except Exception as e:
        print(e)
        return url
    return location



#模拟登陆wait
def dologinwait():
    # ssl._create_default_https_context = ssl._create_unverified_context
    url='https://wait.la/user-login.htm'
    header = {'Accept': 'text/plain, */*; q=0.01',
              'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
              'Origin': 'https://wait.la',
              'Referer': 'https://wait.la/user-login.htm',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
              }

    data = {
        'email': '2982208622@qq.com',
        'password': '837420a5a8fa8f71fd263351e1539601'
    }
    result=re.post(url,verify=False,data=data,headers=header).text
    soup = BeautifulSoup(result, 'html.parser')
    if soup.select(".card-title"):
        ok=soup.select(".card-title")[0].text
        if ok.strip()=='登录成功':
            print('login ok!')
        else:
            print('login error!')



#获取产品详情
def getdealdetail(dealurl):
    url='https://wait.la/collectproduct.htm'   #wait.la 获取shopfipy商品详情链接，（抓包获取）
    data = {
        'collect-url': 'collect-url',
        'url': dealurl
    }
    header = {'Accept': 'text/plain, */*; q=0.01',
              'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
              'Origin': 'https://wait.la',
              'Referer': 'https://wait.la/crawl.htm',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
              'x-requested-with':'XMLHttpRequest',
              'accept-encoding':'gzip, deflate, br'
              }
    result = {}
    try:
        # print(data)
        resultdata = re.post(url, verify=False, data=data, headers=header).text
        # print(resultdata)
        resultdict=json.loads(resultdata)
        # print(resultdict)
        if resultdict['code']=='0':
            message=resultdict['message']
            # result['name']=message['title']
            if message['title'] =='' or message['title'] is None:
                return result
            result['name'] = message['title']
            result['description']=str(base64.b64encode(message['body_html'].encode(encoding='utf-8')), encoding = 'utf-8')
            result['price']=message['price']
            #获取产品图片字符串
            images=message['images']
            if images =='' or images is None:
                return result
            imgst=''
            for image in images:
                imgst = imgst + image['src'] + "||"
            result['images']  = imgst[:-2]
            #获取分类
            options=message['options']
            optiondict = {}
            for option in options:
                optiondict[option['name']]={}
                values=option['values']
                for value in values:
                    optiondict[option['name']][value]=result['price']
            result['product_option']=json.dumps(optiondict)
    except Exception as e:
        print('get shopfipydealdetail error!')
        print(e)
    return result

while(True):
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    #读取自建站
    sites=[]
    with open("site.json", 'r') as load_f:
        sites=json.load(load_f)
    print(sites)
    #模拟登陆
    # print("start login..")
    # dologinwait()
    #获取要抓取的页面url
    print('start get datalist')
    urls=getData()
    print('data length:%s'%(len(urls)))
    print(urls)
    #存放自建站数据
    mysites=[]
    for urldict in urls:
        if urldict['sitename'] in sites:
           mysites.append(urldict)
           continue

        url=urldict['url']
        try:
            if 'https://' not in url and 'http://' not in url:
                url = 'https://' + url
            if 'bit.ly' in url:
                realurl = revertShortLink(url)  # 将短链接换成长链接
            else:

                req = requests.get(url)
                realurl=req.url
        except Exception as e:
            print(e)
            updatestatus(3,urldict['id'])  # 将状态修改为失败状态3
            continue
        print('start crawl--turl：'+realurl)

        # print('start crawl--longurl：'+url)
        print('get dealdetail...')
        result=getdealdetail(realurl)
        # print('dealdetail:',result)
        if len(result)!=0:
            result['dealid']=urldict['id']
            insertDealdetatilData(result)
            updatestatus(2, urldict['id'])   #获取商品详情成功
        else:
            updatestatus(3,urldict['id'])   #将状态修改为失败状态3
        print('sleep 3s...\n')
        time.sleep(5)   #睡眠5秒防止太频繁被封

    print('excuting mysites:\n'+str(mysites))
    #自建站数据单独处理
    for site in mysites:
        sitename = site['sitename']
        url = site['url']
        id=site['id']
        modulename = 'pull' + sitename.lower()
        if url==None:
            continue
        try:
            module = __import__(modulename)
            parser = getattr(module, modulename)(url)
            result = parser.formatdeal()
            # print(result)
            if result !={}:
                result['dealid'] = id
                insertDealdetatilData(result)
                updatestatus(2, id)  # 获取商品详情成功
            else:
                updatestatus(3, id)  # 将状态修改为失败状态3
        except Exception as e:
            updatestatus(3, id)  # 将状态修改为失败状态3
            print(e)
        time.sleep(5)


    db.close()  # 关闭数据库连接
    print("sleeping 5*60.....")
    time.sleep(5*60)


if __name__ == '__main__':
    url="https://hotvideobuy.com/products/cleaner-23";
    print(getdealdetail(url))