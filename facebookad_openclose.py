#coding:utf8
# pip install BeautifulSoup4
# pip install urllib3
# pip install requests
# pip install selenium

from bs4 import BeautifulSoup
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
#from UnicodeCsv import *
import json
import time
import codecs
import urllib
import datetime
import MySQLdb
import MySQLdb.cursors
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

cfg = "facebookad.cfg"
API_VERSION = "v3.1"

def loadCfg(cfg):
    with codecs.open(cfg, 'r', encoding='utf8') as myfile: data = myfile.read()
    o = json.loads(data)
    token = o['token']
    accounts = o["accounts"]

    list = []
    for item in accounts:
        a = {}
        a["id"] = item["id"]
        a["max-cost"] = item["max-cost"]

        list.append(a)

    return [token, list]

def lodmysql():
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    cursor = db.cursor()
    sql = "select id,token from cod_admin where status=1 and username='储一峰'"
    list = []
    token=''
    try:
        cursor.execute(sql)
        results = cursor.fetchone()
        id=results[0]
        token = results[1]
        try:
            accountcursor=db.cursor()
            accountsql="select account_id,max_cost from accounts where flag=1 and userid="+bytes(id)
            print accountsql
            accountcursor.execute(accountsql)
            accounts = accountcursor.fetchall()
            for account in accounts:
                a = {}
                account_id=account[0]
                maxcost=account[1]
                a["id"]=account_id
                a["max-cost"]=maxcost
                list.append(a)
        except:
            print "Error: unable to fecth accountsad"
        finally:
            accountcursor.close()
    except:
        print "Error: unable to fecth defaultdata"
    finally:
        cursor.close()
    return [token, list]


def getAccountInsight(accountid, accessToken):
    # https://developers.facebook.com/docs/marketing-api/insights/parameters
    url = "https://graph.facebook.com/" + API_VERSION + "/act_" + accountid + "/insights""?access_token=" + accessToken + "&action_attribution_windows=default&date_preset=today&time_range={'since':'2018-07-01','until':'2018-07-28'}&fields=cpc,cpm,clicks,cost_per_action_type,account_name,action_values,actions"
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        data = o['data']
        #print d;
    except Exception, e:
        print(e.message)

    return ''

def getAllBussiness(accessToken):
    url = "https://graph.facebook.com/" + API_VERSION + "/me/businesses?access_token=" + accessToken
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        data = o['data']
        list = []
        for item in data:
            id = item["id"]
            name = item["name"]
            list.append([id, name])
        #print d;
        return list
    except Exception, e:
        print(e.message)

    return []

def getAllCampaigns(accountid, accessToken):
    url = "https://graph.facebook.com/" + API_VERSION + "/act_"+ accountid+"/campaigns?access_token=" + accessToken + "&fields=name,configured_status,objective&effective_status=['ACTIVE']&limit=200"
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        data = o['data']
        list = []
        for item in data:
            id = item["id"]
            name = item["name"]
            status = item["configured_status"]
            obj = item["objective"]
            list.append([id, name, status, obj])
        #print d;
        return list
    except Exception, e:
        print(e.message)

    return []


def getAllActiveAdSet(campaignsid, accessToken):
    url = "https://graph.facebook.com/" + API_VERSION + "/"+ campaignsid+"/adsets?access_token=" + accessToken + "&fields=name,configured_status,bid_strategy,daily_budget,promoted_object,created_time,status,source_adset,source_adset_id,optimization_goal&effective_status=['ACTIVE']&limit=200&date_preset=today"
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        data = o['data']
        list = []
        for item in data:
            id = item["id"]
            name = item["name"]
            status = item["configured_status"]
            budget = item["daily_budget"]
            bid = item["bid_strategy"]
            created_time = item["created_time"]
            source_adset_id = item["source_adset_id"]
            obj = item["promoted_object"]
            pixel = obj["pixel_id"]
            event_type = obj['custom_event_type']
            list.append([id, name, status, budget, created_time, bid, source_adset_id, pixel, event_type])
        #print d;
        return list
    except Exception, e:
        print(e.message)

    return []

def getAllPauseAdSet(campaignsid, accessToken):
    url = "https://graph.facebook.com/" + API_VERSION + "/"+ campaignsid+"/adsets?access_token=" + accessToken + "&fields=name,configured_status,bid_strategy,daily_budget,promoted_object,created_time,status,source_adset,source_adset_id,optimization_goal&effective_status=['PAUSED']&limit=200&filtering=[{'field':'impressions','operator':'GREATER_THAN', 'value':'0'}]&date_preset=today"
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        data = o['data']
        list = []
        for item in data:
            id = item["id"]
            name = item["name"]
            status = item["configured_status"]
            budget = item["daily_budget"]
            bid = item["bid_strategy"]
            created_time = item["created_time"]
            source_adset_id = item["source_adset_id"]
            obj = item["promoted_object"]
            pixel = obj["pixel_id"]
            event_type = obj['custom_event_type']
            list.append([id, name, status, budget, created_time, bid, source_adset_id, pixel, event_type])
        #print d;
        return list
    except Exception, e:
        print(e.message)

    return []

def getAllActiveAdSetByAccount(accountid, accessToken):
    url = "https://graph.facebook.com/" + API_VERSION + "/act_"+ accountid +"/adsets?access_token=" + accessToken + "&fields=name,configured_status,bid_strategy,daily_budget,promoted_object,created_time,status,source_adset,source_adset_id,optimization_goal&effective_status=['ACTIVE']&limit=200&filtering=[{'field':'impressions','operator':'GREATER_THAN', 'value':'0'}]&date_preset=today"
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        data = o['data']
        list = []
        for item in data:
            id = item["id"]
            name = item["name"]
            status = item["configured_status"]
            if "daily_budget" in item:
                budget = int(item["daily_budget"])
            else:
                budget = 0
            bid = item["bid_strategy"]
            created_time = item["created_time"]
            source_adset_id = item["source_adset_id"]
            obj = item["promoted_object"]
            pixel = obj["pixel_id"]
            event_type = obj['custom_event_type']

            list.append([id, name, status, budget, created_time, bid, source_adset_id, pixel, event_type])
        #print d;
        return list
    except Exception, e:
        print(e.message)

    return []

def getAllPauseAdSetByAccountid(accountid, accessToken):
    url = "https://graph.facebook.com/" + API_VERSION + "/act_"+ accountid +"/adsets?access_token=" + accessToken + "&fields=name,configured_status,bid_strategy,daily_budget,promoted_object,created_time,status,source_adset,source_adset_id,optimization_goal&effective_status=['PAUSED']&limit=500&filtering=[{'field':'impressions','operator':'GREATER_THAN', 'value':'100'}]&date_preset=today"
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        data = o['data']
        list = []
        for item in data:
            id = item["id"]
            name = item["name"]
            status = item["configured_status"]
            if "daily_budget" in item:
                budget = int(item["daily_budget"])
            else:
                budget = 0
            bid = item["bid_strategy"]
            created_time = item["created_time"]
            source_adset_id = item["source_adset_id"]
            obj = item["promoted_object"]
            pixel = obj["pixel_id"]
            event_type = obj['custom_event_type']
            list.append([id, name, status, budget, created_time, bid, source_adset_id, pixel, event_type])
        #print d;
        return list
    except Exception, e:
        print(e.message)

    return []

def getAdSetInsights(adsetids, accessToken):

    list = []
    for id in adsetids:
        list.append(["GET", id+"/insights?fields=adset_id,cpc,cpm,actions,action_values,cost_per_action_type,buying_type,account_name,adset_name,campaign_name,ctr,frequency,impressions,objective,spend&date_preset=today"])
    #url = "https://graph.facebook.com/" + API_VERSION + "/"+ adsetid+"/insights?access_token=" + accessToken + "&fields=cpc,cpm,actions,action_values,cost_per_action_type,buying_type,account_name,adset_name,campaign_name,ctr,frequency,impressions,objective,spend&date_preset=today"
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        #c = requests.get(url, header)
        list = batchRequest(token, list)
        ret = []
        for d in list:
            try:
                o = json.loads(d)
                data = o['data']
                for item in data:
                    id = item["adset_id"]
                    name = item["adset_name"]
                    campname = item['campaign_name']
                    buying_type = item["buying_type"]
                    ctr = item["ctr"]
                    frequency = item["frequency"]
                    impressions = item["impressions"]
                    if impressions != '':
                        impressions = int(impressions)
                    else:
                        impressions = 0

                    objective = item["objective"]
                    spend = float(item["spend"])
                    if "cpc" in item:
                        cpc = float(item["cpc"])
                    else:
                        cpc = 0.0
                    cpm = float(item["cpm"])

                    addToCartNum = 0
                    checkoutNum = 0
                    purchaseNum = 0
                    puschase = 0.0
                    costPerPuschase = 0.0

                    if "actions" in item:
                        actions = item["actions"]
                        for i in actions:
                            key = i["action_type"]
                            value = i["value"]
                            if key == 'offsite_conversion.fb_pixel_add_to_cart':
                                if value != '':
                                    addToCartNum = int(value)
                                else:
                                    addToCartNum = 0
                            elif key == 'offsite_conversion.fb_pixel_initiate_checkout':
                                if value != '':
                                    checkoutNum = int(value)
                                else:
                                    checkoutNum = 0
                            elif key == 'offsite_conversion.fb_pixel_purchase':
                                if value != '':
                                    purchaseNum = int(value)
                                else:
                                    purchaseNum = 0

                    if "action_values" in item:
                        action_values = item["action_values"]
                        for i in action_values:
                            key = i["action_type"]
                            value = i["value"]
                            if key == 'offsite_conversion.fb_pixel_purchase':
                                puschase = float(value)

                    if "cost_per_action_type" in item:
                        cost_per_action_type = item["cost_per_action_type"]
                        for i in cost_per_action_type:
                            key = i["action_type"]
                            value = i["value"]
                            if key == 'offsite_conversion.fb_pixel_purchase':
                                costPerPuschase = float(value)

                    ret.append([id, name, campname, spend, addToCartNum, checkoutNum, purchaseNum, puschase, costPerPuschase, impressions, frequency, buying_type, ctr, cpc, cpm, objective])
                #print d;
            except Exception, e1:
                print(e1.message)
        return ret
    except Exception, e:
        print(e.message)

    return []

def duplicateAdSet(adsetid, accessToken):
    url = "https://graph.facebook.com/" + API_VERSION + "/"+ adsetid+"/copies?access_token=" + accessToken
    nowTime = datetime.datetime.now().strftime('%Y%m%d %H:%M')
    suffix = "t[" + nowTime + "]"
    payload = {"deep_copy": "true", "rename_suffix": suffix, "status_option": "ACTIVE"}
    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.post(url, data=urllib.urlencode(payload), headers = header)
        d = c.content
        o = json.loads(d)
        #print d;
    except Exception, e:
        print(e.message)


def updateAdSet(adsetid, accessToken, budget, status):
    url = "https://graph.facebook.com/" + API_VERSION + "/"+ adsetid+"?access_token=" + accessToken
    if budget > 0:
        budget = budget # converto US dallor to cents
        payload = {"daily_budget": budget, "status": status}
    else:
        payload = {"status":status}

    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.post(url, data=urllib.urlencode(payload), headers = header)
        d = c.content
        o = json.loads(d)
        print d;
    except Exception, e:
        print(e.message)

    return ''

def batchRequest(accessToken, list):
    url = "https://graph.facebook.com/"+ API_VERSION + "?access_token=" + accessToken

    list2 = []
    for item in list:
        list2.append({"method":item[0], "relative_url":item[1]})

    payload = {"batch": json.dumps(list2)}

    header = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              # 'Content-Length': '65',
              'Content-type': 'application/x-www-form-urlencoded',
              'Host': 'graph.facebook.com',
              'Origin': 'https://developers.facebook.com',
              'Referer': 'https://developers.facebook.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.post(url, data=urllib.urlencode(payload), headers = header)
        d = c.content
        o = json.loads(d)
        list = []
        for item in o:
            if "body" in item:
               list.append(item["body"])
        return list
    except Exception, e:
        print(e.message)

    return []


def getMaxCost(str):
    try:
        str = str.lower()
        str = str.replace("c【","c[").replace("】","]").replace("d【","d[").replace("a【","a[").replace("b【","b[")

        if str.find('c[') != -1:
           start = str.find('c[')
           start = start + 2
           end = str.find(']', start)
           sub = str[start:end]
           dotindex = sub.find('.')
           if dotindex > 0:
              f = float(sub)
              cost = int(f)
           else:
              cost = int(sub)
           return cost
        elif str.find('d[') != -1:
            start = str.find('d[')
            start = start + 2
            end = str.find(']', start)
            sub = str[start:end]
            dotindex = sub.find('.')
            if dotindex > 0:
                f = float(sub)
                cost = int(f)
            else:
                cost = int(sub)
            return cost
        elif str.find('b[') != -1:
            start = str.find('b[')
            start = start + 2
            end = str.find(']', start)
            sub = str[start:end]
            dotindex = sub.find('.')
            if dotindex > 0:
                f = float(sub)
                cost = int(f)
            else:
                cost = int(sub)
            return cost
        elif  str.find('a[') != -1:
            start = str.find('a[')
            start = start + 2
            end = str.find(']', start)
            sub = str[start:end]
            dotindex = sub.find('.')
            if dotindex > 0:
               f = float(sub)
               cost = int(f)
            else:
               cost = int(sub)
            return cost
        else:
            return 0     
    except Exception, e:
        #print(e.message)
        ''

    return 0

def getSkipUpdateBudget(str):
    try:
        str = str.lower()
        str = str.replace("d【","d[").replace("】","]")
        start = str.find('d[')
        if start != -1:
           skip = True
        else:
           skip = False
        return skip
    except Exception, e:
        #print(e.message)
        ''

    return False

def getSkipAll(str):
    try:
        str = str.lower()
        str = str.replace("a【","a[").replace("】","]")
        start = str.find('a[')
        if start != -1:
           skip = True
        else:
           skip = False
        return skip
    except Exception, e:
        #print(e.message)
        ''

    return False

def getSkipNew(str):
    try:
        str = str.lower()
        str = str.replace("b【","b[").replace("】","]")
        start = str.find('b[')
        if start != -1:
           skip = True
        else:
           skip = False
        return skip
    except Exception, e:
        #print(e.message)
        ''

    return False


while(True):
    print ("Start : %s" % time.ctime())
    account = lodmysql()
    token = account[0]
    list = account[1]
    print token
    print list
    for account in list:
        print ("Time : %s" % time.ctime())
        try:
            id = account["id"]
            defaultmaxcost = account["max-cost"]
            #getAccountInsight(id, token)
            #getAllBussiness(token)
            #campList = getAllCampaigns(id, token)
            #cid = campList[1][0]

            adsetlist1 = getAllActiveAdSetByAccount(id, token)
            adsetlist2 = getAllPauseAdSetByAccountid(id, token)

            inactiveList = [];
            activeList = []
            budgetMap = {}
            adsetIds = []
            for i in adsetlist1:
                id = i[0]
                budget = i[3]
                budgetMap[id] = budget
                adsetIds.append(id)

            if len(adsetIds) > 50:
                count = 0
                tmpList = []
                for id in adsetIds:
                    count = count + 1
                    tmpList.append(id)
                    if count >= 50:
                        l = getAdSetInsights(tmpList, token)
                        activeList.extend(l)
                        count = 0
                        tmpList = []

                l = getAdSetInsights(tmpList, token)
                activeList.extend(l)
            else:
                l = getAdSetInsights(adsetIds, token)
                activeList.extend(l)

            adsetIds = []
            for i in adsetlist2:
                id = i[0]
                budget = i[3]
                budgetMap[id] = budget
                adsetIds.append(id)
                #l = getAdSetInsights(id, token)
                #inactiveList.extend(l)

            if len(adsetIds) > 50:
                count = 0
                tmpList = []
                for id in adsetIds:
                    count = count + 1
                    tmpList.append(id)
                    if count >= 50:
                        l = getAdSetInsights(tmpList, token)
                        activeList.extend(l)
                        count = 0
                        tmpList = []

                l = getAdSetInsights(tmpList, token)
                inactiveList.extend(l)
            else:
                l = getAdSetInsights(adsetIds, token)
                inactiveList.extend(l)

            #print inactiveList
            #print activeList
            for item in activeList:
                id = item[0]
                name = item[1]
                campname = item[2]
                spend = item[3]
                addToCartNum = item[4]
                purchaseNum = item[6]
                purchase = item[7]
                costPerPuschase = item[8]
                budget = budgetMap[id]
                
                skipAll = getSkipAll(name)
                skipNew = getSkipNew(name)
                skipupdateBudget = getSkipUpdateBudget(name)
                maxcost = getMaxCost(name)

                if skipAll == False:
                   skipAll = getSkipAll(campname)

                if skipNew == False:
                   skipNew = getSkipNew(campname)

                if skipupdateBudget == False:
                   skipupdateBudget = getSkipUpdateBudget(campname)


                if maxcost == 0:
                    maxcost = getMaxCost(campname)

                if maxcost <= 0:
                    maxcost = defaultmaxcost

                close = False

                if budget > 600000:
                    close = True

                if purchaseNum >= 5 and costPerPuschase > maxcost * 1.5:
                    close = True

                if skipAll == False and skipNew == False:
                    if spend > 30.0 and purchaseNum < 1:
                        close = True
                
                if skipAll == False:
                    if spend > maxcost * 0.5:
                        if purchaseNum < 1:
                            close = True
 
                if skipAll == False:
                    if costPerPuschase > maxcost * 0.8:
                        close = True

                if close == True:
                    updateAdSet(id, token, 0, "PAUSED")
                    print ('close adset:' + name + ", id =" + id)

                if skipupdateBudget == False and skipAll == False:
                    if costPerPuschase < maxcost * 0.7 and purchaseNum >= 2:
                        if costPerPuschase < maxcost * 0.5:
                            if budget < 500000 and purchaseNum >= 5:
                                updateAdSet(id, token, 500000, "ACTIVE")
                                print ("update budget 5000 adset:" + name + ", id =" + id + ", camp:" + campname)
                            elif budget < 200000:
                                updateAdSet(id, token, 200000, "ACTIVE")
                                print ("update budget 2000 adset:" + name + ", id =" + id + ", camp:" + campname)
                        elif budget < 500000 and purchaseNum >= 10:
                            updateAdSet(id, token, 500000, "ACTIVE")
                            print ("update budget 5000 adset:" + name + ", id =" + id + ", camp:" + campname)
                        elif budget < 300000 and purchaseNum >= 5:
                            updateAdSet(id, token, 300000, "ACTIVE")
                            print ("update budget 3000 adset:" + name + ", id =" + id + ", camp:" + campname)
                        elif budget < 100000 and purchaseNum >= 2:
                            updateAdSet(id, token, 100000, "ACTIVE")
                            print ("update budget 1000 adset:" + name + ", id =" + id + ", camp:" + campname)

            for item in inactiveList:
                id = item[0]
                name = item[1]
                campname = item[2]
                spend = item[3]
                addToCartNum = item[4]
                purchaseNum = item[6]
                purchase = item[7]
                costPerPuschase = item[8]

                maxcost = getMaxCost(name)
                if maxcost == 0:
                    maxcost = getMaxCost(campname)

                if maxcost <= 0:
                    maxcost = defaultmaxcost

                skipAll = getSkipAll(name)
                if skipAll == False:
                    skipAll = getSkipAll(campname)

                open = False
                if purchaseNum > 0:
                    if costPerPuschase < maxcost * 0.75:
                        open = True

                if open == True and skipAll == False:
                    updateAdSet(id, token, 0, "ACTIVE")
                    print ("open adset:" + name + ", id =" + id)

            #adsetid = adsetlist[0][0]
            #insights = getAdSetInsights(adsetid, token)
            #adsetid = "23842836078360125"

            #updateAdSet(adsetid, token, 0, "PAUSED")
            #updateAdSet(adsetid, token, 1, "ACTIVE")
        except Exception, e:
            print(e.message)
    time.sleep(5 * 60)
