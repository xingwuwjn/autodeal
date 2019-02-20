# coding: utf-8
import base64
import re
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
import memcache
import requests
from contextlib import closing
import hashlib

global browser
# browser = webdriver.Chrome()
def create_id():
    m = hashlib.md5(str(time.clock()).encode('utf-8'))
    return m.hexdigest()


#插入数据
def insertdata(resultall):
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    for result in resultall:
        siteid=result['siteid']
        likes=result['likes']
        views = result['views']
        comments = result['comments']
        shares = result['shares']
        url=repr(result['url'])
        adsurl = repr(result['adsurl'])
        dealurl = repr(result['dealurl'])
        name = repr(result['name'])
        title = repr(result['title'])
        countryid = result['countryid']
        posttime = result['posttime']
        message = repr(result['message'])
        firstimage = repr(result['firstimage'])
        video=repr(result['video'])
        images=repr(result['images'])
        cursor = db.cursor()
        insert_sql = """
                       insert into pages(siteid,likes,views,comments,shares,url,adsurl,dealurl,name,title,countryid,posttime,message,firstimage,video,images)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                       siteid=%s,likes=%s,views=%s,comments=%s,shares=%s,url=%s,adsurl=%s,dealurl=%s,name=%s,title=%s,countryid=%s,posttime=%s,message=%s,images=%s
                   """ %(siteid,likes,views,comments,shares,url,adsurl,dealurl,name,title,countryid,posttime,message,firstimage,video,images,siteid,likes,views,comments,shares,url,adsurl,
                         dealurl,name,title,countryid,posttime,message,images)
        try:
            print(insert_sql)
            cursor.execute(insert_sql)
            db.commit()
            print('insert update successed!')
            cursor.close()
        except Exception as e:
            print (e)

    db.close()



#获取竞争对手的站点配置
def getData():
    db = MySQLdb.connect("localhost", "root", "wwwcodcom", "station", charset='utf8')
    select_sql="select name,countryid,id from sites where flag=1"
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



def pgads(result):

    if (len(result) == 0):
        print('All have been collected, try again later')
        time.sleep(5)
    else:
        print('set language..')
        try:
            main = 'https://www.facebook.com'
            browser.get(main)
            time.sleep(5)
            browser.find_element_by_css_selector("a[lang='en_US']").click()
            time.sleep(5)
            browser.find_element_by_class_name("layerConfirm").click()
            print('set ok')
        except Exception as e:
            print(e)
            print("language is english")
        #连接memcached,抓取过的不在抓取
        mc = memcache.Client(['127.0.0.1:11211'], debug=True)

        for key,url in result.items():
            # countryarray = []
            # url=result[item]
            name = url[0]
            countryid = url[1].strip()
            siteid=url[2]
            countryarray = countryid.split(",")
            if len(countryarray) == 0:
                countryarray.append(0)
                countryarray.append(1)
                countryarray.append(3)
            try:
                for country in countryarray:
                    if country=='':
                        continue
                    path = 'https://www.facebook.com/pg/%s/ads/?country=%s' % (name,country)
                    print('Start collecting '+path)
                    browser.get(path)
                    time.sleep(10)
                    # 获取网页内容
                    elem = browser.find_element_by_tag_name("html")
                    js = 'window.scrollTo(0, document.body.scrollHeight);'
                    for i in range(2):
                        print('crawl'+str(i)+'page')
                        browser.execute_script(js)
                        time.sleep(1.5)
                    html = elem.get_attribute('innerHTML')
                    # print(html)
                    # 获取相关信息
                    soup = BeautifulSoup(html, 'html.parser')
                    if soup.select("a[aria-label='Profile picture']"):
                        actor_id = soup.select("a[aria-label='Profile picture']")[0].get("href")
                        actor_id = actor_id.split("/")[1]
                        print(actor_id)
                    if actor_id==None:
                        if soup.select("._2dgj"):
                            actor_id = soup.select("a[aria-label='Profile picture']")[0].get("href")
                            actor_id = actor_id.split("/")[1]
                            print(actor_id)
                    facebookurl = []
                    if soup.select('._5pcp'):
                        for child in soup.select('._5pcp'):
                            feed_subtitle = child.get('id')
                            #多种推广形式
                            feed_subtitle1 = feed_subtitle.split(';')
                            if len(feed_subtitle1) > 2:
                                subid = feed_subtitle1[1]
                            else:
                                subid = feed_subtitle.split(':')[0].split('_')[2]
                            facebookurl.append('https://www.facebook.com/%s/posts/%s' %
                                            (actor_id, subid))    #actor_id(pageid) subid(postid)
                    # 采集详情页
                    resultall = []
                    print(facebookurl)
                    for postpath in facebookurl:
                        if mc.get(postpath) is not None:
                            print("%s is crawled"%(postpath))
                            continue
                        else:
                            try:
                                # 获取详情内容
                                result = {}
                                # 点赞数
                                result['siteid'] = siteid
                                result['likes'] = 0
                                result['views'] = 0
                                result['comments'] = 0
                                result['shares'] = 0
                                result['url'] = postpath
                                result['adsurl'] = path
                                result['name'] = name
                                result['countryid'] = country
                                result['dealurl'] = ''
                                result['title'] = ''
                                result['firstimage'] = ''
                                result['video'] = ''
                                result['images'] = ''
                                result['message'] = ''
                                print('crawl '+postpath)
                                try:
                                    browser.get(postpath)
                                    time.sleep(2)
                                    postelem = browser.find_element_by_tag_name("html")
                                    posthtml = postelem.get_attribute('innerHTML')

                                except Exception as e:
                                    print('open page error')
                                    print(e)
                                postsoup = BeautifulSoup(posthtml, 'html.parser')
                                print("get html success!")
                                #如果第一个帖子无评论直接返回
                                if len(postsoup.select('._524d')[0].select("._-5d"))<1:
                                    print("first no comments,zan")
                                    # 更新时间和文案
                                    if postsoup.select('._5pbx'):
                                        result['posttime'] = postsoup.select('._5ptz')[0].get(
                                            'data-utime')
                                        result['message'] = repr(postsoup.select('._5pbx')[0])
                                        result['message'] = re.sub("<a.*>.*</a>", "{{}}", result['message'], 0, 0)
                                        result['message'] = re.sub("<[^>]*>|<\/[^>]*>/gm", "", result['message'], 0, 0)
                                        # result['message']=str(result['message']).replace("https://l.facebook.com/l.php?u=", "")
                                        result['message'] = str(
                                            base64.b64encode(result['message'].encode(encoding='utf-8')), encoding='utf-8')
                                    if postsoup.select("._3ekx ._5s6c"):
                                        result['title']=postsoup.select("._3ekx ._5s6c")[0].text
                                    # 投放商品url
                                    if postsoup.select("._3x-2 ._275- ._42ft"):
                                        dealurl = postsoup.select("._3x-2 ._275- ._42ft")[0].get('href')
                                        if 'facebook' not in dealurl:
                                            result['dealurl']=dealurl
                                    #获取商品链接
                                    if postsoup.select('._5pbx a'):
                                        if result['dealurl'] =='':
                                            result['dealurl'] = postsoup.select('._5pbx')[0].select("a").text

                                    if 'https://' not in result['dealurl'] and 'http://' not in result['dealurl']:
                                        result['dealurl'] = 'https://' + result['dealurl']

                                    if postsoup.select("#content_container div[role='main'] ._1xnd ._4-u2"):
                                        # video = str(postsoup.select("._5pcp .fwn a")[0].get("href"))
                                        firstpage = postsoup.select("#content_container div[role='main'] ._1xnd ._4-u2")[0]
                                        if firstpage.select('._27w7 ._27w8'):

                                            ajaxify = firstpage.select('._27w7 ._27w8')[0].get('ajaxify')
                                            videoid = ajaxify.split('&id=')[1].split('&')[0]

                                            videourl = 'https://www.facebook.com/' + actor_id + '/videos/' + videoid + '/'
                                            videohtml = requests.get(videourl)
                                            video_url = re.search('hd_src:"(.+?)"', videohtml.text).group(1)
                                            videopath = "video/" + create_id() + ".mp4"
                                            print('downloading videourl:' + video_url)
                                            download_file(video_url, videopath)
                                            result['video'] = videopath
                                            firstimgpath = "image/" + create_id() + ".jpg"
                                            if firstpage.select("._3chq"):
                                                firstimgurl = firstpage.select("._3chq")[0].get("src")
                                                print('download firstimgurl:' + firstimgurl)
                                                download_file(firstimgurl, firstimgpath)
                                                result['firstimage'] = firstimgpath
                                        else:
                                            print('no video')

                                else:
                                    print("has comments")
                                    #更新时间和标题
                                    if postsoup.select('._5pbx'):
                                        result['posttime'] = postsoup.select('._5ptz')[0].get(
                                            'data-utime')
                                        result['message'] = repr(postsoup.select('._5pbx')[0])
                                        result['message'] = re.sub("<a.*>.*</a>", "{{}}", result['message'], 0, 0)
                                        result['message'] = re.sub("<[^>]*>|<\/[^>]*>/gm", "", result['message'], 0, 0)
                                        # result['message']=str(result['message']).replace("https://l.facebook.com/l.php?u=", "")
                                        result['message']=str(base64.b64encode(result['message'].encode(encoding='utf-8')), encoding='utf-8')
                                        # 投放商品url
                                    if postsoup.select("._3ekx ._5s6c"):
                                        result['title'] = postsoup.select("._3ekx ._5s6c")[0].text

                                    # 投放商品url
                                    if postsoup.select("._3x-2 ._275- ._42ft"):
                                        dealurl = postsoup.select("._3x-2 ._275- ._42ft")[0].get("href")
                                        if 'facebook' not in dealurl:
                                            result['dealurl'] = dealurl
                                    if postsoup.select('._5pbx a'):
                                        if result['dealurl'] =='':
                                            result['dealurl'] = postsoup.select('._5pbx a')[0].text
                                    if 'https://' not in result['dealurl'] and 'http://' not in result['dealurl']:
                                        result['dealurl'] = 'https://' + result['dealurl']
                                    # if postsoup.select("._3x-2 ._275- ._42ft"):
                                    #         result['dealurl'] = postsoup.select("._3x-2 ._275- ._42ft")[0].get('href')
                                    if postsoup.select("#content_container div[role='main'] ._4-u2"):
                                        # video = str(postsoup.select("._5pcp .fwn a")[0].get("href"))
                                        firstpage=postsoup.select("#content_container div[role='main'] ._4-u2")[0]

                                        if firstpage.select('._27w7 ._27w8'):
                                            ajaxify = firstpage.select('._27w7 ._27w8')[0].get('ajaxify')
                                            videoid = ajaxify.split('&id=')[1].split('&')[0]
                                            videourl = 'https://www.facebook.com/' + actor_id + '/videos/' + videoid + '/'

                                            videohtml = requests.get(videourl)
                                            video_url = re.search('hd_src:"(.+?)"', videohtml.text).group(1)
                                            videopath = "video/" + create_id() + ".mp4"
                                            print('downloading videourl:' + video_url)
                                            download_file(video_url, videopath)
                                            result['video'] = videopath
                                            firstimgpath = "image/" + create_id() + ".jpg"
                                            if firstpage.select("._3chq"):
                                                firstimgurl = firstpage.select("._3chq")[0].get("src")
                                                print('download firstimgurl:' + firstimgurl)
                                                download_file(firstimgurl, firstimgpath)
                                                result['firstimage'] = firstimgpath
                                        else:
                                            print('no video')

                                    #点赞数
                                    if postsoup.select('._4arz'):
                                        result['likes'] = postsoup.select('._4arz')[0].text
                                        if 'M' in result['likes']:
                                            result['likes'] = float(result['likes'].replace(
                                                'M', '')) * 1000 * 1000
                                        elif 'K' in result['likes']:
                                            result['likes'] = float(result['likes'].replace(
                                                'K', '')) * 1000
                                    #评论
                                    if postsoup.select('._36_q > ._-56'):
                                        result['comments'] = postsoup.select('._36_q > ._-56')[
                                            0].text.split(' ')
                                        if result['comments'][1] == 'Comments':
                                            result['comments'] = result['comments'][0].replace(',','')
                                        elif result['comments'][1] == 'Comment':
                                            result['comments'] = result['comments'][0].replace(',','')
                                        if 'M' in result['comments']:
                                            result['comments'] = float(result[
                                                'comments'].replace('M', '')) * 1000 * 1000
                                        elif 'K' in result['comments']:
                                            result['comments'] = float(
                                                result['comments'].replace('K', '')) * 1000
                                    #分享次数
                                    if len(postsoup.select('._36_q > ._2x0m')) > 0:
                                        result['shares'] = postsoup.select('._36_q > ._2x0m')[
                                            0].text.split(' ')
                                        if result['shares'][1] == 'Views':
                                            result['views'] = result['shares'][0]
                                            result['shares'] = 0
                                        elif result['shares'][1] == 'Shares':
                                            result['shares'] = result['shares'][0]
                                        else:
                                            result['shares'] = result['shares'][0]
                                        if result['shares'] != 0:
                                            if 'M' in result['shares']:
                                                result['shares'] = float(
                                                    result['shares'].replace('M',
                                                                            '')) * 1000 * 1000
                                            elif 'K' in result['shares']:
                                                result['shares'] = float(
                                                    result['shares'].replace('K', '')) * 1000
                                            elif ',' in result['shares']:
                                                result['shares']=float(
                                                    result['shares'].replace(',', ''))
                                    #播放次数
                                    if result['views'] == 0:
                                        if len(postsoup.select('._36_q > ._2x0m')) > 1:
                                            result['views'] = postsoup.select(
                                                '._36_q > ._2x0m')[1].text.split(' ')
                                            if result['views'][1] == 'Views':
                                                result['views'] = result['views'][0]
                                            elif result['views'][1] == 'Shares':
                                                result['shares']=result['shares'][0]
                                                result['views'] = 0
                                            if result['views'] != 0:
                                                if 'M' in result['views']:
                                                    result['views'] = float(
                                                        result['views'].replace(
                                                            'M', '')) * 1000 * 1000
                                                elif 'K' in result['views']:
                                                    result['views'] = float(
                                                        result['views'].replace('K',
                                                                                '')) * 1000
                                            else:
                                                if result['views'][1] == 'Shares':
                                                    result['shares'] = result['shares'][0]
                                                    result['views']=0
                                                if 'M' in result['views']:
                                                    result['views'] = float(result['views'].replace(
                                                     'M', '')) * 1000 * 1000
                                                elif 'K' in result['views']:
                                                    result['views'] = float(result['views'].replace(
                                                        'K', '')) * 1000

                                    try:
                                        float(result['views'])
                                    except:
                                        result['views']=0

                                    try:
                                        float(result['likes'])
                                    except:
                                        result['likes']=0
                                    # print(result['views'])
                                    # print(result['likes'])

                                    # if float(result['views']) > float(result['likes']):
                                    #     result['views'] = float(result['views'])
                                    # else:
                                    #     result['views'] = float(result['likes']) * 10

                                mc.set(postpath, 'a', 60 * 60 * 24)  # 采集过的设入memcached
                            except Exception as e:
                                # with open('errors.txt', 'a') as f:
                                #     f.write(
                                #         time.strftime('%Y-%m-%d %H:%M:%S',
                                #                     time.localtime(time.time())) +
                                #         'postpath ' + postpath + 'bug：' + str(repr(e)) +
                                #         '\n')
                                print('crawl data error')
                                time.sleep(1)
                                # if (float(result['likes'])>=10) or (float(result['views'])>=3000):


                        if result['video']!='':
                            resultall.append(result)
                    
                    print (resultall)
                    if len(resultall)>0:
                        insertdata(resultall)


            except Exception as e:
                print(e)
                # with open('errors.txt', 'a') as f:
                #     f.write(
                #         time.strftime('%Y-%m-%d %H:%M:%S',
                #                     time.localtime(time.time())) + 'path ' +
                #         path + 'bug：' + str(repr(e)) + '\n')



def download_file(url, path):
    with closing(requests.get(url, stream=True)) as r:
        time.sleep(2)
        chunk_size = 1024 * 10
        content_size = int(r.headers['content-length'])
        print(content_size)
        print ('download start')
        with open(path, "wb") as f:
            p = ProgressData(size=content_size, unit='Kb', block=chunk_size)
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                p.output()


class ProgressData(object):

    def __init__(self, block, size, unit, file_name='', ):
        self.file_name = file_name
        self.block = block / 1000.0
        self.size = size / 1000.0
        self.unit = unit
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
            print ('%s download finished\r\n' % self.file_name)
        # else:
            # print ('{0}下载进度{1:.2f}{2}/{3:.2f}{4} 下载速度{5:.2%} {6:.2f}{7}/s'. \
            #     format(self.file_name, loaded, self.unit, \
            #            self.size, self.unit, progress, speed, self.unit))
            # print ('%50s' % ('/' * int((1 - progress) * 50)))



while(True):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--lang=" + "en-US")
    browser = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
    # browser.delete_all_cookies()
    # browser = webdriver.Chrome()
    # 登录fb
    fblogo()
    tmpsites = getData()
    sites={}
    for site in tmpsites:
        if sites.get(site[0])==None:
            sites[site[0]]=site
    print(sites)
    # 获取需要采集的粉丝页
    pgads(sites)
    print('Continue 1 hour after execution')
    try:
        browser.close()
        print("browser is closed")
    except Exception as  e:
        print(e)
    time.sleep(3*60*60)
