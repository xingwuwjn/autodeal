
import MySQLdb
import MySQLdb.cursors
import requests
import json
from bs4 import BeautifulSoup
import base64

db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')


#获取要爬取的url
def getData():
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql="select b.id,a.dealurl,b.deal_id from pages as a left join facebook_deal as b where a.flag=0 and a.id=b.deal_id "
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
    name=repr(result['name'])
    images=repr(result['images'])
    dealid=repr(result['dealid'])
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

    product_id=int(url.split('product_id=')[1])
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
    c = requests.get(url, header)
    html = c.content
    print(html)
    soup = BeautifulSoup(html, 'html.parser')
    result={}
    if soup.select("#content h1"):
       result['name']=soup.select("#content h1")[0].text
    if soup.select('.price-new-live'):
        result['price']=soup.select('.price-new-live')[0].text
    if soup.select('.image-additional img'):
        imgs=soup.select('.image-additional img')
        for img in imgs:
            imgst=imgst+img.get("src")+"||"
        imglen=len(imgst)- 2
        result['images']=imgst[:-2]
    if soup.select("input[name='product_id']"):
        product_id=int(soup.select("input[name='product_id']")[0].get('value'))

    #获取变种，以及价格
    priceurl='https://www.surprise.shopping/index.php?route=extension/module/live_options&product_id=%d'%(product_id)
    # name:
    # text:
    # option[267]: 156
    # quantity: 1
    # product_id: 112
    if soup.select("#product .control-label"):
        sendidst = soup.select("#product .control-label")[0].get("for")
        sendid = sendidst.split('input-option')[1]
        selectdict={}
        for i in range(len(soup.select("#product .control-label"))):
            selectname=soup.select("#product .control-label")[i].text
            try:
                selecthtml=soup.select("#product select")[i]
            except Exception as e:
                continue
            optionname=selecthtml.get('name')
            options=selecthtml.select('option')
            optiondict={}
            for option in options:
                optionid=option.get('value')
                params = {"name": (None, ''), "text": (None, ''),optionname:(None,optionid),
                          "quantity":(None,1),"product_id":(None,product_id),}
                print(params)
                print(priceurl)
                optionname=option.text.strip()
                res = requests.post(priceurl, files=params)
                print(res.content)
                pricejson=json.loads(res.content)
                optiondict[optionname]=pricejson['new_price']['special']
            selectdict[selectname]=optiondict
        result['product_option']=json.dumps(selectdict)
    if soup.select("#tab-description"):
        result['description']=str(soup.select("#tab-description")[0])
        # result['description']=str(
        #     base64.b64encode(result['description'].encode(encoding='utf-8')), encoding='utf-8')

    result['dealid']=1
    return result

if __name__ == '__main__':
    # urls=getData()
    # for url in urls:
    #     result=pulldels(url)
    #     insertDealdetatilData(result)

    url="https://www.surprise.shopping/index.php?route=product/product&path=63&product_id=112"
    result=pulldels(url)
    insertDealdetatilData(result)