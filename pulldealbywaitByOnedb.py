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

#获取要爬取的url
def getData():

    #获取还未爬取的页面url
    select_sql="""select id,url,category from oc_product_python_add where status=0
                """
    urls=[]
    try:
        dealcursor=db.cursor()
        dealcursor.execute(select_sql)
        deals = dealcursor.fetchall()
        for deal in deals:
            a={}
            id=deal[0]
            url=deal[1]     #url
            category=deal[2]  #产品详情表id
            if url =='' or url is None:
                continue
            a['category']=category
            a['url']=url
            a['id']=id

            urls.append(a)

    except:
        print ("Error: unable to fecth urls")
    finally:
        dealcursor.close()
    return urls



#更新oc_product_python_add状态
def updatestatus(status,id):
    db = MySQLdb.connect(host="50.112.76.240", user="imagedb", db="wwwteststardollscom", passwd="image5v2jHYD", port=4306,
                         charset='utf8')
    select_sql = '''
                   update oc_product_python_add set status=%s where id=%s
                    '''%(status,id)
    # print(select_sql)
    try:
        cursor = db.cursor()
        cursor.execute(select_sql)
        db.commit()
        print('update status=%s,id=%s successed!'%(status,id))
    except:
        print("Error: unable to update status=%s,id=%s"%(status,id))
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

#发送产品数据到api接口
def sendcontent(singledeal):
        singledeal = json.dumps([singledeal])
        # print(singledeal)
        singledeal=str(base64.b64encode(singledeal.encode(encoding='utf-8')), encoding = 'utf-8')
        username='Default'
        key='ffDP4ZLNH7x0KG90lcKlRb9xLhx8mzg5atjWi4bl8dlLBhmXVckhRJT8U2AlBucUzBgs3PyaIqGW9pWG12rfX0l5gzDktynZoVC6erPAK3SfoM5cCj9Zd7z62rNPO1yz23fO4JMK1KW9RumJ9gMYhT8hC2QVh0bNItHEHuMoZOvx7KrG8NO1KO7BmmHr774LjObWTlgqoQ0AwUy60g9OupkHxuKpRLVQn6wI7VPnhQoErYdpacgeFRA1LR8rPeDF'
        datadict={'username':username,'key':key,'data':singledeal}
        re=requests.Session()
        result=re.post('http://www.mystardolls.com/index.php?route=api/toadd&api_token',data=datadict)
        print(result.text)
        print(result.status_code)
        if result.status_code==200:
            try:
                results = json.loads(result.text)
                updatestatus(1, urldict['id'])  # 获取商品详情成功
            except Exception as e:
                updatestatus(2, urldict['id'])  # 获取商品详情失败



while(True):
    db = MySQLdb.connect(host="50.112.76.240", user="imagedb",db="wwwteststardollscom",passwd="image5v2jHYD",port=4306,charset='utf8')
    #模拟登陆
    # print("start login..")
    # dologinwait()
    #获取要抓取的页面url
    print('start get datalist')
    urls=getData()
    print('data length:%s'%(len(urls)))
    print(urls)
    for urldict in urls:
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
            updatestatus(2,urldict['id'])  # 将状态修改为失败状态2
            continue
        print('start crawl--turl：'+realurl)

        # print('start crawl--longurl：'+url)
        print('get dealdetail...')
        result=getdealdetail(realurl)
        print('dealdetail:',result)
        if len(result)!=0:
            a = {}
            # a['oid'] = deal[0]
            a['category'] = urldict['category']
            a['price'] = result['price']
            a['images'] = result['images']
            a['name'] = result['name']
            a['description'] = str(base64.b64decode(result['description']), encoding='utf-8')
            # a['description'] = deal[4]
            # a['description'] = '11'
            options = json.loads(result['product_option'])
            # a['oldurl'] = deal[6]
            c = {}
            c['product_data'] = a
            c['product_option'] = options
            print(c)
            # updatestatus(1, urldict['id'])  # 获取商品详情成功
            sendcontent(c)
        else:
            updatestatus(2,urldict['id'])   #将状态修改为失败状态2
        print('sleep 3s...\n')
        time.sleep(5)   #睡眠5秒防止太频繁被封



    db.close()  # 关闭数据库连接
    print("sleeping 5*60.....")
    time.sleep(5*60)


# if __name__ == '__main__':
#     url="https://hotvideobuy.com/products/cleaner-23";
#     print(getdealdetail(url))