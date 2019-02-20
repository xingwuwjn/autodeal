# coding: utf-8
import requests
import MySQLdb
import MySQLdb.cursors
import json
import time
import base64
from urllib import parse


#获取要爬取的url
def getData():
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql='''
                select b.id,a.price,a.images,a.name,a.description,a.option1,b.dealurl from facebook_deal as a,pages as b 
                where a.deal_id=b.id and b.launch_url is null
                '''
    opencartdeals=[]
    try:
        dealcursor=db.cursor()
        dealcursor.execute(select_sql)
        deals = dealcursor.fetchall()
        for deal in deals:
            a={}
            a['oid']=deal[0]
            a['price']=deal[1]
            a['images']=deal[2]
            a['name']=deal[3]
            a['description']=str(base64.b64decode(deal[4]),encoding = 'utf-8')
            # a['description'] = deal[4]
            # a['description'] = '11'
            options=json.loads(deal[5])
            a['oldurl'] = deal[6]
            c={}
            c['product_data']=a
            c['product_option']=options
            opencartdeals.append(c)

    except:
        print ("Error: unable to fecth urls")
    finally:
        dealcursor.close()
        db.close()
    return opencartdeals


#更新url
def updateurl(url,id):
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql = '''
                   update pages set launch_url=%s where id=%s
                    '''%(url,id)
    # print(select_sql)
    try:
        cursor = db.cursor()
        cursor.execute(select_sql)
        db.commit()
        print('update successed!')
    except:
        print("Error: unable to update url,pageid=%s"%(id))
    finally:
        cursor.close()
        db.close()



while(True):
    print("start get data")
    opencartdeals=getData()
    print('data length:'+str(len(opencartdeals)))
    # print(type(opencartdeals))
    if opencartdeals is not None:
        for singledeal in opencartdeals:
            singledeal = json.dumps([singledeal])
            # print(singledeal)
            singledeal=str(base64.b64encode(singledeal.encode(encoding='utf-8')), encoding = 'utf-8')
            username='Default'
            key='MX44IwfDVdYuin24CKD7CwOpDy1yRQj5yqqv9GsBehPyVAC3wiO8gcIcS024dIZdKlLoRHBoMjB0KipZhCEUhYzfXE4dpk746fJ9BAA1z3N1kOVwgVuGY5JFpRLv8nJvt2ficIYwHuVLbsGYHU5p4NIbP0e13zGIEfaJbjz7nvJVNQsRY7uCfcTwuWjEPKkZlIQjzZGZnk2x9WCjTmZ7JAzrrPINfZLOsxd9ZO8FI3wC9u9pBmGQswE4wSNVVMJj'
            datadict={'username':username,'key':key,'data':singledeal}
            re=requests.Session()
            result=re.post('https://www.1daydreamer.com/index.php?route=api/toadd&api_token',data=datadict)
            print(result.text)
            print(result.status_code)
            if result.status_code==200:
                try:
                    results = json.loads(result.text)
                    # print(results)
                    datas=results['data']
                    # print(datas)
                    for data in datas:
                        id = data['oid']
                        url = data['url']
                        url = parse.unquote(url)
                        updateurl(repr(url), id)
                except Exception as e:
                    print('error resultdata')
    print("sleep 1*60....")
    time.sleep(1*60)