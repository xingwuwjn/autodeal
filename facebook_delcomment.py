#coding:utf8
# pip install BeautifulSoup4
# pip install urllib3
# pip install requests

from bs4 import BeautifulSoup
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
#from UnicodeCsv import *
import json
import time
import codecs
import urllib
import MySQLdb
import MySQLdb.cursors
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
API_VERSION="v3.1"


def loadmysql():

    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    cursor = db.cursor()
    delList = []
    sql="select * from chart_defaultkey"
    try:

        cursor.execute(sql)
        results = cursor.fetchall()
        for defaultrow in results:
            name = defaultrow[1]
            delList.append(name)
    except:
        print "Error: unable to fecth defaultdata"
    finally:
        cursor.close()
    postsql="select * from chart_posts where flag=0 and post_group='营销二部' "
    try:
        postscrusor=db.cursor()
        postscrusor.execute(postsql)
        postresults = postscrusor.fetchall()
        postList = []
        for row in postresults:
            postid=row[0]
            print 'fecthed----'+postid
            post = {}
            keyList=delList[:]
            try:
                increasesql="select name from chart_increasedkey where postid="+bytes(postid)
                increasecursor=db.cursor()
                increasecursor.execute(increasesql)
                increaseresults=increasecursor.fetchall()
                for increaserow in increaseresults:
                    if increaserow[0].strip() != '':
                        keyList.append(increaserow[0])
            except:
                print "Error: unable to fecth increasedkeydata"
            finally:
                increasecursor.close()
            post["id"] = postid
            post["delkey"] = keyList
            post["max"] = row[1]
            post["first"] = row[2]
            post["pageid"] = row[4]
            post["postid"] = row[5]
            post["token"] = row[6]
            post["check"] = row[7]
            post["initreply"] = row[8]

            autokeyList = []
            autoreplyList = []
            try:
                autoreplysql = "select name,content from chart_autoreply where postid="+bytes(postid)
                print(autoreplysql)
                autoreplycursor = db.cursor()
                autoreplycursor.execute(autoreplysql)
                autoreplyresults = autoreplycursor.fetchall()
                if len(autoreplyresults):
                    for autorow in autoreplyresults:
                        autokeyList.append(autorow[0].strip())
                        autoreplyList.append(autorow[1].strip())
            except:
                print "Error: unable to fecth autoreplydata"
            finally:
                autoreplycursor.close()
            post["key"] = autokeyList
            post["reply"] = autoreplyList
            cursor.close();
            postList.append(post)
    except:
            print "Error: unable to fecth posttdata"
    finally:
        postscrusor.close()


    return postList



def getPageAccessToken(pageid, accessToken):
    url = "https://graph.facebook.com/me/accounts?accessToken=" + accessToken + "&debug=all&format=json&method=get&pretty=0&suppress_http_code=1"
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
        for item in data:
            id = item['id']
            name = item['name']
            token = item['access_token']
            list.append([id, name, token])
            if id == pageid:
                return token
    except Exception, e:
        print(e.message)

    return ''

def getAllComment(pageid,postid, accessToken, next = ''):
    #url = "https://graph.facebook.com/" + postid + "/comment?access_token=" + accessToken + "&fields=id,from,message,created_time&order=chronological"
    url = "https://graph.facebook.com/"+API_VERSION+"/" + pageid+"_"+postid + "/comments?access_token=" + accessToken + "&fields=can_hide,message,is_hidden,id,from,created_time,attachment&limit=100&order=reverse_chronological"
    if next.strip() != '':
        url = next

    header={'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            #'Content-Length': '65',
            'Content-type': 'application/x-www-form-urlencoded',
            'Host': 'graph.facebook.com',
            'Origin': 'https://developers.facebook.com',
            'Referer': 'https://developers.facebook.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}

    # print "get comment:" + postid
    list = []
    next = ''
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        if o.has_key("paging"):
            next = o['paging']
            if next.has_key("next"):
                next = next['next']
            else:
                next = ''

        data = o['data']
        for item in data:
            time = item['created_time']
            message = item['message']
            id = item['id']
            is_hidden = item["is_hidden"]
            can_hidden = item["can_hide"]
            #att = item['attachment']
            if "attachment" in item:
                has_att = True
            else:
                has_att = False
            list.append([id, message, time, is_hidden, can_hidden, has_att])
    except Exception, e:
        print(e.message)

    return [list, next]

def publishComment(postid, message, accessToken):
    url = "https://graph.facebook.com/"+API_VERSION+"/"+ postid + "/comments?message=" + message + "&access_token=" + accessToken

    header={'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            #'Content-Length': '65',
            'Content-type': 'application/x-www-form-urlencoded',
            'Host': 'graph.facebook.com',
            'Origin': 'https://developers.facebook.com',
            'Referer': 'https://developers.facebook.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.post(url, header)
        d = c.content
    except Exception, e:
        print(e.message)

def replyComment(postid, message, accessToken):
    url = "https://graph.facebook.com/"+API_VERSION+"/" + postid + "/comments?access_token=" + accessToken
    payload = {"debug":"all","format":"json","message":message, "method":"post","pretty":0,"suppress_http_code":1}
    header={'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            #'Content-Length': '65',
            'Content-type': 'application/x-www-form-urlencoded',
            'Host': 'graph.facebook.com',
            'Origin': 'https://developers.facebook.com',
            'Referer': 'https://developers.facebook.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    try:
        c = requests.post(url, data=urllib.urlencode(payload), headers = header)
        d = c.content
    except Exception, e:
        print('reply error')
        print(e.message)

def deleteComment(commentid, accessToken):
    url = "https://graph.facebook.com/"+API_VERSION+"/" + commentid + "?access_token=" + accessToken

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
        c = requests.delete(url)
        d = c.content
        print(d)
    except Exception, e:
        print('delete error--'+e.message)

def hideComment(commentid, accessToken):
    url = "https://graph.facebook.com/"+API_VERSION+"/" + commentid + "?access_token=" + accessToken + "&is_hidden=true"

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
        c = requests.post(url)
        d = c.content
    except Exception, e:
        print('hide error--'+e.message)



def getComment(commentid, accessToken,next):
    url = "https://graph.facebook.com/" + API_VERSION + "/" + commentid + "/comments?access_token=" + accessToken + "&fields=can_hide,message,is_hidden,id,from,created_time,attachment&limit=100&order=reverse_chronological"
    if next.strip() != '':
        url = next

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

    # print "get comment:" + postid
    list = []
    next = ''
    try:
        c = requests.get(url, header)
        d = c.content
        o = json.loads(d)
        if o.has_key("paging"):
            next = o['paging']
            if next.has_key("next"):
                next = next['next']
            else:
                next = ''

        data = o['data']
        for item in data:
            time = item['created_time']
            message = item['message']
            id = item['id']
            is_hidden = item["is_hidden"]
            can_hidden = item["can_hide"]
            # att = item['attachment']
            if "attachment" in item:
                has_att = True
            else:
                has_att = False
            list.append([id, message, time, is_hidden, can_hidden, has_att])
    except Exception, e:
        print(e.message)

    return [list, next]


def processComment(post, isfirst):
    i = 0
    allList=[]
    next=''
    accessToken = post["token"]
    maxNum = post["max"]
    firstNum = post["first"]
    postid = post["postid"]
    pageid = post["pageid"]
    checkPublish = post["check"]
    publishMessage = post["initreply"]
    delList = post["delkey"]

    keyList = post["key"]
    replyList = post["reply"]


    if isfirst == True:
        maxNum = firstNum

    #accessToken = getPageAccessToken(pageid, userAccessToken)
    if accessToken.strip() == '':
        print('can not get token, please check the post id, pageid, userAccessToken')
    #获取一级评论
    while(i < maxNum ):
        l = getAllComment(pageid,postid, accessToken, next)
        i += len(l[0])
        next = l[1]

        allList.extend(l[0])
        isStr = isinstance(next, basestring)

        if isStr == False:
            break;

        if next.strip() == '':
            break

    print 'get 1_conmment_'+str(len(allList))


    #deleteComment('231400674287269_243206326440037', accessToken)
    twoleveList=[]
    relyL = []
    for item in allList:
        id = item[0]
        message = item[1]
        is_hidden = item[3]
        can_hidden = item[4]
        has_att = item[5]
        message = message.strip()
        message = message.lower()
        # print(message.encode("GB18030", "ignore"))
        delete = False


        if is_hidden == True:
            continue

        if has_att == True:
            if message == '':
                delete = True
            elif checkPublish in message:
                delete = False
            else:
                delete = True
        elif message != '':
            for word in delList:
                if word in message:
                    delete = True
                    break
        # print(delete)
        if delete == True:
            try:
                if can_hidden == True:
                    hideComment(id, accessToken)
                    print("hide message:" + message.encode("GB18030", "ignore"))
                else:
                    deleteComment(id, accessToken)
                    print("delete message:" + message.encode("GB18030", "ignore"))
            except Exception, e:
                print('delete&hide error')
        else:
            twoleveList.append(id)
            for i in range(0, len(keyList)):
                key = keyList[i].lower()
                reply = replyList[i]
                if key in message:
                    try:
                        #replyComment(id, reply, accessToken)
                        relyL.append([0, id, reply])
                    except Exception, e:
                        print('add autoreplay error')

    # delete two level comments获取二级评论
    print('filter-'+str(len(twoleveList)))
    twoAllList=[]
    for id in twoleveList:
        l = getComment(id, accessToken, '')
        twoAllList.append([id,l[0]])

    # print('get 2_comment_' + str(len(twoAllList)))
    # flag={}
    for item in twoAllList:
        addcom = True
        parentId = item[0]
        comList = item[1]
        # addcom = True
        # flag[parentId]=False

        if len(comList) > 0:
            for item2 in comList:
                id = item2[0]
                message = item2[1]
                is_hidden = item2[3]
                can_hidden = item2[4]
                has_att = item2[5]

                message = message.lower()
                message = message.strip()
                delete = False

                if is_hidden == True:
                    continue

                if checkPublish in message:
                    # flag[parentId]=True
                    addcom = False
                    print('replyed-'+str(parentId))

                if has_att == True:
                    if message == '':
                        delete = True
                    elif checkPublish in message:
                        delete = False
                    else:
                        delete = True
                elif message != '':
                    for word in delList:
                        if word.strip() != '' and word in message:
                            delete = True
                            break

                if delete == True:
                    print("delete message:" + message.encode("GB18030","ignore"))
                    try:
                        if can_hidden:
                            hideComment(id, accessToken)
                        else:
                            deleteComment(id, accessToken)
                    except Exception, e:
                        print(e.message)
                #else:
                    #for i in range(0, len(keyList)):
                    #    key = keyList[i]
                    #    reply = replyList[i]
                    #    if key in message:
                    #        try:
                                #replyComment(id, reply, accessToken)
                    #            relyL.append([parentId, id, reply])
                    #        except Exception, e:
                    #            print(e.message)

        for item3 in relyL:
            reply = False
            id = item3[1]
            r = item3[2]
            if parentId == id:
                reply = True

            if len(comList) > 0:
                for item4 in comList:
                    message = item4[1]
                    if r in message:
                        reply = False
                        break

            if reply == True:
                replyComment(id, r, accessToken)
                print('autoreplay-'+id)
                addcom=False

        if addcom == True:
            try:
                replyComment(parentId, publishMessage, accessToken)
                print('initreplay-'+parentId)
                time.sleep(5)
            except Exception, e:
                print('reply error!')


first = True
while(True):
    postList = loadmysql()
    # print postList
    print ("Start : %s" % time.ctime())
    for item in postList:
        print 'excuting-'+item['id']+time.ctime()
        try:
            processComment(item, first)
        except Exception, e:
            print(e.message)
        print 'excuted-' + item['id']+time.ctime()+"\n"
    print ("End : %s" % time.ctime())

    first = False
    print('slepping.....')
    time.sleep(120)
