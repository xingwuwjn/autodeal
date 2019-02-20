# coding: utf-8
import requests
import json
import os
import time
import MySQLdb
import MySQLdb.cursors
import base64

#获取要上品的产品
def getdata():
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql = '''
                    select id,adset,launch_country,gender,age,budget,campaign_name,video,name,message,title,firstimage,launch_url,area from
                     measureproduct where launch_status=0
                    '''
    deals = ()
    try:
        dealcursor = db.cursor()
        dealcursor.execute(select_sql)
        deals = dealcursor.fetchall()
        print(deals)

    except:
        print("Error: unable to fecth measureproduct")
    finally:
        dealcursor.close()
        db.close()
    return deals

def gettokens():
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql = '''
                    select id,account,access_token,pageid,pixel_id,area,instagram_actor_id from tokens
                    '''
    deals = ()
    try:
        dealcursor = db.cursor()
        dealcursor.execute(select_sql)
        deals = dealcursor.fetchall()
        print(deals)

    except:
        print("Error: unable to fecth tokens")
    finally:
        dealcursor.close()
        db.close()
    return deals


#getcampain
def getcampain(account_id,access_token):
    # account_id=''
    # access_token=''
    url='https://graph.facebook.com/v3.1/act_'+account_id+'/campaigns?'
    header1 = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    payload={'fields':'name,configured_status,objective','effective_status':"['PAUSED']",'limit':200,
            'access_token':access_token}
    try:
        c = requests.get(url,params=payload)
        print(c.url)
        d = c.content
        print(d)
        o = json.loads(d)
        print(o)
    except Exception as e:
        print(e)
        print('create campain error')


#更新url
def updatestatus(status,id):
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql = '''
                   update measureproduct set launch_status=%s where id=%s
                    '''%(status,id)
    # print(select_sql)
    try:
        cursor = db.cursor()
        cursor.execute(select_sql)
        db.commit()
        print('update status successed!')
    except:
        print("Error: unable to update status,id=%s"%(id))
    finally:
        cursor.close()
        db.close()


#create campain
def createcampain(account_id,name,access_token):
    createurl = "https://graph.facebook.com/v3.1/act_" + account_id + "/campaigns"
    objective='CONVERSIONS'   #enum{APP_INSTALLS, BRAND_AWARENESS, CONVERSIONS, EVENT_RESPONSES, LEAD_GENERATION, LINK_CLICKS, LOCAL_AWARENESS, MESSAGES, OFFER_CLAIMS, PAGE_LIKES, POST_ENGAGEMENT, PRODUCT_CATALOG_SALES, REACH, VIDEO_VIEWS}
    status='PAUSED'
    access_token=access_token
    bid_strategy='LOWEST_COST_WITHOUT_CAP'    #enum{LOWEST_COST_WITHOUT_CAP, LOWEST_COST_WITH_BID_CAP, TARGET_COST}
    payload = {
        'objective': objective,
        'status': status,
        'access_token': access_token,
        'name': name
    }
    campainid=0
    try:
        c=requests.post(createurl,payload)
        d=c.content
        o = json.loads(d)
        print(o)
        campainid=o['id']
        print('create campain successed!\n')
    except Exception as e:
        print(e)
        print('create campain error,please checkout access_token...\n ')
    return campainid


#delete campain
def deletecampain(campain_id,access_token):
    url="https://graph.facebook.com/v3.1/"+campain_id+"/?access_token="+access_token
    try:
        c=requests.delete(url)
        d=c.content
        o = json.loads(d)
        if o['success']:
            print('delete campain successed!\n')
    except Exception as e:
        print(e)
        print('delete campain error,please checkout access_token...\n ')

#create adset
def createadset(instagram_actor_id,name,account_id,campaign_id,access_token,pixel_id,age_min,age_max,gender,daily_budge,countryarray):
    adseturl='https://graph.facebook.com/v3.1/act_'+account_id+'/adsets'
    name=name
    daily_budget=daily_budge*100   #每日预算
    campaign_id=campaign_id    #系列名称
    # destination_type='WEBSITE'
    pixel_id=pixel_id    #像素id
    countryarray=countryarray    #投放国家

    targeting={}
    targeting['geo_locations']={"countries":countryarray,"location_types": ['recent', 'home']}
    targeting['age_min']=age_min    #最小年龄
    targeting['age_max']=age_max    #最大年龄
    if gender == '男':
        targeting['genders'] = [1]  # 性别男
    if gender == '女':
        targeting['genders'] = [2]  # 性别女

    targeting['device_platforms']=["mobile"]
    targeting['publisher_platforms']=["facebook","instagram"]
    targeting['facebook_positions']=["feed"]
    targeting['instagram_positions']=["stream"]

    status='PAUSED'
    access_token=access_token
    # bid_amount='1'
    billing_event='IMPRESSIONS'
    # optimization_goal='REACH'
    # end_time='2018-09-21T15:41:30+0000'
    # lifetime_budget='100000'
    payload = {'name': name,
               'status': status,
               'access_token': access_token,
               'daily_budget': daily_budget,
               'campaign_id': campaign_id,
               'billing_event':billing_event,
               'instagram_actor_id':instagram_actor_id,
               'bid_strategy':'LOWEST_COST_WITHOUT_CAP',
               'targeting':str(targeting),
               # 'destination_type':destination_type,
               'promoted_object':str({"pixel_id":pixel_id,"custom_event_type":"PURCHASE"}),
               "attribution_spec": str([
                   {
                       "event_type": "VIEW_THROUGH",
                       "window_days": 1
                   },
                   {
                       "event_type": "CLICK_THROUGH",
                       "window_days": 7
                   }
               ])
               }
    adsetid=0
    try:
        c=requests.post(adseturl, params=payload)
        d=c.content
        o = json.loads(d)
        print(o)
        adsetid=o['id']
    except Exception as e:
        print(e)
        print('create adset error!\n')
    return adsetid



#create ad
def createad(name,account_id,adset_id,access_token,creative_id):
    adurl='https://graph.facebook.com/v3.1/act_'+account_id+'/ads'
    adset_id=adset_id
    status='PAUSED'
    access_token=access_token
    creative='{"creative_id":"'+creative_id+'"}'
    payload={
        'name':name,
        'adset_id':adset_id,
        'creative':creative,
        'status':status,
        'access_token':access_token
    }
    print(payload)
    c=requests.post(adurl,payload)
    d = c.content
    o = json.loads(d)
    adid = o['id']
    return adid


#create adcreatives
def createadcreatives(instagram_actor_id,creativatename,account_id,access_token,page_id,video_data):
    url='https://graph.facebook.com/v3.1/act_'+account_id+'/adcreatives'
    name=creativatename
    object_story_spec={}
    object_story_spec['page_id']=page_id
    object_story_spec['video_data']=video_data
    # object_story_spec['link_data']=link_data
    payload = {
        'name':name,
        'object_story_spec':str(object_story_spec),
        'access_token': access_token,
        'title':creativatename,
        'description':creativatename,
        'body':creativatename,
        'instagram_actor_id':instagram_actor_id
    }
    print(payload)
    creative_id=0
    try:
        r = requests.post(url,payload)
        d = r.content
        o = json.loads(d)
        print(o)
        creative_id=o['id']
        print('create adcreative successed\n')
    except Exception as e:
        print(e)
        print('create adcreatives error!\n')
    return creative_id


#upload video
def uploadvideo(pageid,filename,access_token):
    data = {'access_token': access_token,
            'title': 'hello  video title! ',
            'description': 'hello video description!'
            }
    file_path = filename
    url='https://graph-video.facebook.com/v3.1/'+pageid+'/videos'
    files = {
        'files':(filename, open(file_path, 'rb'), 'text/plain'),
    }
    videoid=0
    try:
        r = requests.post(url, files=files ,data=data)
        d = r.content
        o = json.loads(d)
        print(o)
        videoid=o['id']
        print('first image,video successed!\n')
    except Exception as e:
        print(e)
        print('upload video %s error!\n'%(filename))
    return videoid




while(True):
    deals=getdata()
    tokens=gettokens()
    areastoken={}
    for item in tokens:
        areastoken[item[5]]=item
    # print(areastoken)

       # #账户id
    # account_id = '544482746008191'
    # # access_token = 'EAAD9vNVq7O0BALvDhDFPqHZB0cCiWouEgntNHTSG3IlLI34ZCFouRv8YcE3HJswLijA3rzoKLbtGjAxJ5rZBvEJzHsArq5vXXZAOg9qVEl2ZBDlg4lIV7C2lJRpLWsb5KZAUqrJ40sb8BXtAZCPcXuSZBzNVxMNZBB0Mo5qvA5LQb9QZDZD'
    #
    # #主页token
    # access_token='EAAD5lmZBjrpEBANm4ZBlZBZBW25ZC25GcCIHLyDQrV1gV0GIubpQlkZA2pZAyTjCx7w64KBdLEyuTZAKwqvkTIYvDTu2irHGARexbwCY9yTmRCmRUMQBZA0LrnUDTeGmtPNZCuImcrqn2eeyHuBz6wzXa3C7ZBTGhJzqrBXZCzdwUuhpIwZDZD'
    # #主页id
    # pageid = '329607517584699'
    # #像素id
    # pixel_id = "262293747732018"

    # getinstagramurl='https://graph.facebook.com/v3.1/'+pageid+'/instagram_accounts?access_token='+access_token
    # print(getinstagramurl)
    # insaccount=requests.get(getinstagramurl)
    # print(insaccount.text)

    for deal in deals:
        id=deal[0]
        adset=deal[1]    #广告组
        launch_country=deal[2]   #投放国家
        gender=deal[3]    #性别
        age=deal[4]       #年龄
        daily_budget=deal[5]    #每日预算
        campainname=deal[6]   #广告系列名称
        videoname=deal[7]      #视频地址
        dealname=deal[8]
        message=str(base64.b64decode(deal[9]), encoding='utf-8') #投放文案
        title=deal[10]     #标题
        firstimageurl=deal[11]    #视频第一张图片
        launch_url=deal[12]      #投放url
        area=deal[13]       #所属组

        #获取当前组的token等
        try:
            tokenitem=areastoken.get(area)
            account_id=tokenitem[1]
            access_token=tokenitem[2]
            pageid=tokenitem[3]
            pixel_id=tokenitem[4]
            instagram_actor_id=tokenitem[6]
        except  Exception as e:
            continue
        if account_id==None or access_token==None or pageid==None or pixel_id==None or instagram_actor_id==None:
            continue
        message = message.replace("{{}}",launch_url)

        age_min=age.split("-")[0]   #最小年龄
        age_max = age.split("-")[1]   #最大年龄

        adsetname=campainname
        creativatename=campainname
        try:

            #如果文案，投放链接，视频为空，则不进行投放
            if message=='' or launch_url=='' or videoname=='' :
                continue
            #定义国家
            countryarray = []
            countryarray.append(launch_country)

            #创建系列
            print('creating campain....')
            campainid=createcampain(account_id,campainname,access_token)
            if campainid == 0:
                updatestatus(2, id)  # 上品失败
                continue

            #创建广告组
            print('creating adset...')
            adsetid=createadset(instagram_actor_id,adsetname,account_id, campainid, access_token, pixel_id, age_min, age_max, gender, daily_budget,
                        countryarray)
            if adsetid == 0:
                updatestatus(2, id)  # 上品失败
                continue
            #上传图片视频
            print('upload image,video...')
            videoid=uploadvideo(pageid,videoname,access_token)
            if videoid == 0:
                updatestatus(2, id)  # 上品失败
                continue
            #组装视频参数
            video_data={}
            video_data['image_url']=firstimageurl
            video_data['video_id']=str(videoid)
            video_data['call_to_action']={}
            video_data['call_to_action']['type']="LEARN_MORE"
            video_data['call_to_action']['value']={
                     "link": launch_url
            }
            video_data['title']=title
            video_data['message']=message
            # video_data['link_description']='link description'
            #睡眠60秒等待facebook处理
            print("wait facebook excute,sleepping 60s..")
            time.sleep(100)
            #创建素材
            print("createadreatives...")
            creative_id=createadcreatives(instagram_actor_id,creativatename,account_id, access_token, pageid, video_data)
            if creative_id == 0:
                updatestatus(2, id)  # 上品失败
                deletecampain(campainid,access_token)  #删除广告系列
                continue

            #创建广告
            print('creating ad...')
            adid=createad(dealname,account_id, adsetid, access_token, creative_id)
            if adid!=0:
                updatestatus(1,id)   #上品成功
        except Exception as e:
            print(e)
            updatestatus(2,id)  # 上品失败

        time.sleep(1)
    # print("sleepping.. 60")
    time.sleep(60)








