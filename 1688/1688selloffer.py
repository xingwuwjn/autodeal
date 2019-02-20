# coding: utf-8
# In[2]:
import json
from selenium import webdriver
import time
from urllib import parse
from bs4 import BeautifulSoup
import MySQLdb
import MySQLdb.cursors
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
# In[3]:

global browser

#插入数据
def insertdata(results):
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    for result in results:
        offerid=repr(result['offerid'])
        title = repr(result['title'])
        img = repr(result['img'])
        url = repr(result['url'])
        tradebt = repr(result['tradebt'])
        currencyid=repr(result['currencyid'])
        keyword = repr(result['keyword'])
        fromname = repr(result['fromname'])
        create_time = repr(result['create_time'])
        cursor = db.cursor()
        insert_sql = """
                           insert into alibaba_deal(offerid,title,img,url,tradebt,currencyid,keyword,fromname,create_time)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                           title=%s,img=%s,url=%s,tradebt=%s,currencyid=%s,keyword=%s,fromname=%s,create_time=%s
                       """ %(offerid,title,img,url,tradebt,currencyid,keyword,fromname,create_time,title,img,url,tradebt,currencyid,keyword,fromname,create_time)
        print(insert_sql)
        try:
            cursor.execute(insert_sql)
            db.commit()
            print('insert update deal successed!')
            cursor.close()
        except Exception as e:
                print (e)

    db.close()

#插入商品详情数据
def insertDealdetatilData(result):
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    offerid=repr(result['offerid'])
    name=repr(result['name'])
    success_num = repr(result['success_num'])
    comment_num = repr(result['comment_num'])
    logo = repr(result['logo'])
    create_time = repr(result['create_time'])
    seller_region = repr(result['seller_region'])
    province = repr(result['province'])
    city = repr(result['city'])
    seller_name = repr(result['seller_name'])
    seller_url = repr(result['seller_url'])
    price = result['price']
    origin_price = result['origin_price']
    currencyid = repr(result['currencyid'])
    keywords=repr(result['keywords'])
    detaildesc = repr(result['detaildesc'])
    fromname = repr(result['fromname'])
    interval_price = repr(result['interval_price'])
    body = repr(result['body'])
    prop = repr(result['prop'])
    inventory = repr(result['inventory'])
    comment = repr(result['comment'])
    img = repr(result['img'])
    url = repr(result['url'])
    cursor = db.cursor()
    insert_sql = """
                         insert into alibaba_dealdetail(offerid,name,success_num,comment_num,logo,create_time,seller_region,province,
                         city,seller_name,seller_url,price,origin_price,currencyid,keywords,detaildesc,fromname,interval_price,
                         body,prop,inventory,comment,img,url)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                         name=%s,success_num=%s,comment_num=%s,logo=%s,create_time=%s,seller_region=%s,province=%s,
                       city=%s,seller_name=%s,seller_url=%s,price=%f,origin_price=%f,currencyid=%s,keywords=%s,
                       detaildesc=%s,fromname=%s,interval_price=%s,body=%s,prop=%s,inventory=%s,comment=%s,img=%s,
                       url=%s
                   """ %(offerid,name,success_num,comment_num,logo,create_time,seller_region,province,
                       city,seller_name,seller_url,price,origin_price,currencyid,keywords,detaildesc,fromname,interval_price,
                       body,prop,inventory,comment,img,url,name,success_num,comment_num,logo,create_time,seller_region,province,
                       city,seller_name,seller_url,price,origin_price,currencyid,keywords,detaildesc,fromname,interval_price,
                       body,prop,inventory,comment,img,url)
    print(insert_sql)
    try:
            cursor.execute(insert_sql)
            db.commit()
            print('insert update dealdetail successed!')
            cursor.close()
    except Exception as e:
                print (e)

    db.close()


#获取阿里巴巴爬取配置信息
def getData():
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql="select name,area from alibabapullkeys where flag=1"
    sites=()
    try:
        sitecursor=db.cursor()
        sitecursor.execute(select_sql)
        sites = sitecursor.fetchall()
    except:
        print ("Error: unable to fecth sites")
    finally:
        sitecursor.close()
        db.close()
    return sites


# In[5]:
def getdeals(keyword):
    browser.get('https://www.1688.com')
    # url = ["咖啡杯", 1, ["江苏", "浙江", "华南区", "华东区"]]
    xuanpinname = 'selloffer'
    values = {}
    word = keyword[0]
    province =keyword[1]
    print (province)
    values['descendOrder'] = 'true'
    values['sortType'] = 'va_rmdarkgmv30'
    values['uniqfield'] = 'userid'
    values['priceEnd'] = 80
    # if province:
    #     if len(province)>0 and province[0]!='所有地区':
    #         province= ','.join(province)
    values['province']=province.encode('gb2312')
    try:
        values['keywords'] = word.encode('gb2312')
    except:
        values['keywords'] = word
    urlvalues = parse.urlencode(values)
    path = 'https://s.1688.com/%s/offer_search.htm?%s'%(xuanpinname,urlvalues)
    print('开始采集' + path)
    browser.get(path)

        # In[1]:


    elem = browser.find_element_by_tag_name("html")
    #滚屏到
    js = "var q=document.documentElement.scrollTop=100000"
    browser.execute_script(js)
    time.sleep(1)
    html = elem.get_attribute('innerHTML')
    # In[19]:


    # id = keyword[1]
    results = []
    soup = BeautifulSoup(html, 'html.parser')
    for child in soup.select('.sm-offer-item'):
        resultoffer = {}

        if ('detail.1688.com' in child.select('.sm-offer-photo > a')[0].get(
                'href')):
            resultoffer['url'] = child.select('.sm-offer-photo > a')[0].get(
                'href')
            resultoffer['offerid'] = resultoffer['url'].split('/')[4].split(
                '.')[0]
        else:
            break

        if (child.select('.sm-offer-photo > a')):
            resultoffer['title'] = child.select('.sm-offer-photo > a')[0].get(
                'title')
        else:
            resultoffer['title'] = 0
            # 获取商品图片
        if (child.select('.sm-offer-photo > a > img')[0].get('src')):
            resultoffer['img'] = child.select('.sm-offer-photo > a > img')[
                0].get('src')
        else:
            resultoffer['img'] = child.select('.sm-offer-photo > a > img')[
                0].get('data-lazy-src')

        if child.select('.s-widget-offershopwindowdealinfo > .first > i'):
            resultoffer['price'] = child.select('.s-widget-offershopwindowdealinfo > .first > i')[0].get('title')
        elif child.select('.s-widget-offershopwindowprice > .sm-offer-priceNum'):
            resultoffer['price'] = child.select(
                '.s-widget-offershopwindowprice > .sm-offer-priceNum')[0].get(
                'title')
        else:
            resultoffer['price'] = 0

        if ('¥' in resultoffer['price']):
            resultoffer['price'] = resultoffer['price'].replace("¥", "")
        else:
            resultoffer['price'] = 0

        if ('~' in resultoffer['price']):
            resultoffer['price'] = resultoffer['price'].split('~')[1]

        if child.select('.sm-offer-tradeBt'):
            if child.select('.sm-offer-tradeBt')[0].get('data-gmv'):
                resultoffer['tradebt'] = child.select('.sm-offer-tradeBt')[
                    0].get('data-gmv')
            else:
                resultoffer['tradebt'] = child.select('.sm-offer-tradeBt')[
                    0].get('title').replace("30天成交", "").replace("万元", "")

        else:
            resultoffer['tradebt'] = 0
        resultoffer['currencyid'] = 'CNY'
        resultoffer["keyword"] = keyword[0]
        # resultoffer["searchid"] = keyword[1]
        resultoffer["fromname"] = '1688'
        resultoffer["create_time"] = int(time.time())
        results.append(resultoffer)
    return results

def innerHTML(element):
    return element.decode_contents(formatter="html")

# 商品页面
def grap_html(url):
    elem = browser.find_element_by_tag_name("html")
    js = 'window.location.hash = "#desc-lazyload-container";'
    browser.execute_script(js)
    time.sleep(0.2)
    ret = check_loading_thing(60, 0.5)
    if not ret:
        return grap_html(url)
    html = elem.get_attribute("innerHTML")
    return parse_html(html, url)

# 加载中
def check_loading_thing(timeout, onetime):
    if not is_element_exist("#desc-lazyload-container"):
        time.sleep(3)
    tfir = 0
    while True:
        time.sleep(onetime)
        tfir += onetime
        if (
            not browser.find_element_by_id("desc-lazyload-container").get_attribute(
                "innerHTML"
            )
            == "加载中..."
        ):
            return True
        if tfir > timeout:
            print("timeout")
            return False
        break


# 判断元素是否存在
def is_element_exist(css):
    s = browser.find_elements_by_css_selector(css_selector=css)
    if len(s) == 0:
        # print("元素未找到：",css)
        return False
    elif len(s) >= 1:
        # print("存在元素：",css)
        return True



def parse_html(html, url):
    id = ""
    if html == "":
        return
    result = {}
    soup = BeautifulSoup(html, 'html.parser')
    if soup.select("#mod-detail-title > .d-title"):
        result["name"] = str(soup.select("#mod-detail-title > .d-title")[0].text)
    else:
        result["name"] = ""

    if soup.select(".bargain-number > a > em"):
        result["success_num"] = str(soup.select(".bargain-number > a > em")[0].string)
    elif soup.select(".bargain-number > a > .amount-red"):
        result["success_num"] = str(
            soup.select(".bargain-number > a > .amount-red")[0].string
        )
    else:
        result["success_num"] = 0

    if soup.select(".satisfaction-number > a > em"):
        result["comment_num"] = str(
            soup.select(".satisfaction-number > a > em")[0].string
        )
    elif soup.select(".satisfaction-number > a > .amount-red"):
        result["comment_num"] = str(
            soup.select(".satisfaction-number > a > .amount-red")[0].string
        )
    else:
        result["comment_num"] = 0

    result["logo"] = []
    for child in soup.select(".nav-tabs > li"):
        result["logo"].append(json.loads(child.get("data-imgs"))["original"])
    result["logo"] = json.dumps(result["logo"], ensure_ascii=False)
    result["create_time"] = int(time.time())

    # 获取商家联系方式

    if soup.select(".delivery-detail > .delivery-addr"):
        result["seller_region"] = str(
            soup.select(".delivery-detail > .delivery-addr")[0].string
        )
        seller_region = result["seller_region"].split(" ")
        if len(seller_region) > 1:
            result["province"] = seller_region[0]
            result["city"] = seller_region[1]
        else:
            result["province"] = seller_region[0]
            result["city"] = seller_region[0]

    if soup.select(".base-info > a"):
        result["seller_name"] = str(soup.select(".base-info > a")[0].string)
        result["seller_url"] = soup.select(".base-info > a")[0].get("href")
    if soup.find(attrs={"property": "og:product:price"})["content"]:
        result["price"] = soup.find(attrs={"property": "og:product:price"})["content"]
        result["price"] = float(result["price"].split("-")[0])

        result["origin_price"] = soup.find(attrs={"property": "og:product:orgprice"})[
            "content"
        ]
        result["origin_price"] = float(result["origin_price"].split("-")[0])

    else:
        result["price"] = 0
        result["origin_price"] = 0

    result["currencyid"] = soup.find(attrs={"property": "og:product:currency"})[
        "content"
    ]

    result["keywords"] = soup.find(attrs={"name": "keywords"})["content"]

    result["detaildesc"] = soup.find(attrs={"name": "description"})["content"]

    # 商品区间价格
    result["interval_price"] = []
    for child in soup.select(".price > td"):
        if child.get("data-range"):
            result["interval_price"].append(json.loads(child.get("data-range")))
    if len(result["interval_price"]) == 0:
        if soup.select(".price > td > .price-original-sku > .value"):
            price_value = soup.select(".price > td > .price-original-sku > .value")
            if len(price_value) == 2:
                price = str(price_value[1].string)
            else:
                price = str(price_value[0].string)
            ebgin_value = str(soup.select(".amount > td > .value")[0].string)
            ebgin_value_split = ebgin_value.split("≥")
            if len(ebgin_value_split) == 2:
                begin = ebgin_value_split[1]
            else:
                begin = ebgin_value
            end = ""
            result["interval_price"].append(
                {"begin": begin, "end": end, "price": price}
            )
    result["interval_price"] = json.dumps(result["interval_price"], ensure_ascii=False)
    # 详情
    body = innerHTML(soup.select("#desc-lazyload-container")[0])
    result["body"] = body.replace('"', "'")

    result["prop"] = []
    obj = {}
    if soup.select("#mod-detail-attributes"):
        lens = len(soup.select("#mod-detail-attributes")[0].find_all("td"))
        i = 0
        for child in soup.select("#mod-detail-attributes")[0].find_all("td"):
            i = i + 1
            if i != lens:
                if child.get("class")[0] == "de-feature":
                    feature = child.get_text()
                if child.get("class")[0] == "de-value":
                    obj["feature"] = feature
                    obj["value"] = child.get_text()
                    result["prop"].append(obj)

    result["prop"] = json.dumps(result["prop"], ensure_ascii=False)
    # 库存多库存情况
    result["spec"] = []
    result["inventory"] = []
    objleading = {}
    objsku = {}
    if (not soup.select(".obj-leading")) or (not soup.select(".obj-sku")):
        result["inventory"] = []
        # raise Exception('sku error')
    if soup.select(".obj-leading"):
        objleading["attr_name"] = soup.select(
            ".obj-leading > .obj-header > .obj-title"
        )[0].get_text()
        objleading["list"] = []
        for child in soup.select(".list-leading > li > div"):
            obj = {}
            if child.has_attr("data-unit-config"):
                obj["value_name"] = json.loads(child.get("data-unit-config"))["name"]
            # if child.has_attr('data-imgs'):
            # 	obj["img"] = json.loads(child.get('data-imgs'))['original']
            objleading["list"].append(obj)
        result["inventory"].append(objleading)

    if soup.select(".obj-sku"):
        objsku["attr_name"] = soup.select(".obj-sku > .obj-header > .obj-title")[
            0
        ].get_text()
        objsku["list"] = []
        for child in soup.select(".table-sku > tbody > tr"):
            obj = {}
            if child.get("data-sku-config"):
                obj["value_name"] = json.loads(child.get("data-sku-config"))["skuName"]
                # obj["store"] = json.loads(child.get('data-sku-config'))['max']
                # if child.find_all('span',limit=1)[0].has_attr('data-imgs'):
                # 	obj["img"] = json.loads(child.find_all('span',limit=1).get('data-imgs'))['original']
                # else:
                # 	obj["img"] = ""
                # obj['img'] = json.loads(child.get('data-imgs'))['original']
            objsku["list"].append(obj)
        result["inventory"].append(objsku)
    result["inventory"] = json.dumps(result["inventory"], ensure_ascii=False)
    # 评论输出
    result["comment"] = ""
    result["commentarr"] = []
    if soup.select(".bargain-number .value"):
        try:
            result["tradebt"] = soup.select(".bargain-number .value")[0].text
        except Exception as e:
            print (e)
            result["tradebt"]=0
    else:
        result["tradebt"] = 0
    for child in soup.select("#commentbody > .fd-clr > dd > .comment-content"):
        # 判断字数超过20个子的评论
        if len(child.select("p")[0].encode("utf-8")) > 60:
            result["commentarr"].append(child.select("p"))
            result["comment"] += str(child.select("p")[0])
    result["comment"] = result["comment"].replace("<p>", "<li>")
    result["comment"] = result["comment"].replace("</p>", "</li>")
    result["comment"] = "<ol>" + result["comment"] + "</ol>"
    result["offerid"] = url.split("/")[4].split(".")[0]
    result["detailid"] = 0
    result["searchid"] = 0
    result["keyword"] = 0
    result["img"] = json.loads(result["logo"])[0]
    # result["tradebt"] = 0
    result["url"] = url
    result["fromname"] = "1688"
    return result
    # resultsearch = []
    # # 开始保存到数据库中
    # if len(result) > 1:
    #     pymysql.insert_detail(result, id)
    #     resultoffer = {}
    #     resultoffer["url"] = url
    #     resultoffer["title"] = result["name"]
    #     resultoffer["offerid"] = result["offerid"]
    #     resultoffer["img"] = result["img"]
    #     resultoffer["price"] = result["price"]
    #     resultoffer["tradebt"] = result["tradebt"]
    #     resultoffer["currencyid"] = "CNY"
    #     resultoffer["keyword"] = result["keyword"]
    #     resultoffer["searchid"] = result["searchid"]
    #     resultoffer["fromname"] = result["fromname"]
    #     resultoffer["status"] = 2
    #     resultoffer["create_time"] = int(time.time())
    #     resultsearch.append(resultoffer)
    #     pymysql.insert_search(resultsearch, id)
    # else:
    #     pass


def collectdetail(url):
    result={}
    try:
        if "1688" in url:
            url = url.replace("\r", "").replace("\n", "").replace("\t", "")
            print("开始采集" + url)
            browser.get(url)
            result=grap_html(url)
    except Exception as e:
        with open("errors.txt", "a") as f:
            f.write(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                + "bug："
                + str(repr(e))
                + "\n"
            )

    time.sleep(0.01)
    return result
            # time.sleep(2)



while(True):
    keywords = getData()#获取所有的关键词

    for keyword in keywords:
        print(keyword)
        browser = webdriver.Chrome()
        resultoffer=getdeals(keyword)
        insertdata(resultoffer)
        for result in resultoffer:
            url = result['url']
            dealdetail=collectdetail(url)
            insertDealdetatilData(dealdetail)
    time.sleep(30*60)