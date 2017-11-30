import re
#from _md5 import md5
from hashlib import  md5
import  requests
import pymongo
from urllib.parse import urlencode
import os
import time
from pyquery import PyQuery as pq
from requests.exceptions import ConnectionError
from lxml.etree import XMLSyntaxError
from config import *
from urllib3.exceptions import LocationParseError
client=pymongo.MongoClient(MONGO_URL)
db=client[MONGO_DB]
base_url='http://weixin.sogou.com/weixin?'
index_url=None
headers={
'Cookie':'CXID=AE0C75530B202F4A020D5998070D236F; IPLOC=CN3201; ld=skllllllll2zRvkylllllVo23xllllllGU9xlkllll9lllll9llll5@@@@@@@@@@; SUV=00B21787314101025A0D2811330D8443; pgv_pvi=4667037696; pgv_si=s391035904; ABTEST=7|1511423816|v1; weixinIndexVisited=1; JSESSIONID=aaa5QGyouX1pw7CJZXv8v; ppinf=5|1511423928|1512633528|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTUlOEUlOUYlRTglOTElOTd8Y3J0OjEwOjE1MTE0MjM5Mjh8cmVmbmljazoxODolRTUlOEUlOUYlRTglOTElOTd8dXNlcmlkOjQ0Om85dDJsdUNESkhPVGRwOXR1OVVDT01IY0wzUkVAd2VpeGluLnNvaHUuY29tfA; pprdig=o5auIGf5wm-ELmDtZQMX95GoAsIV1Q8uaXs5Ty_94Iz4AG6bw5DKd691uRhicPMMfMApLJ74Hw1PLbFdGfMaDqCz3H186lEsGJQTZE_7LrxoIQPanP7xgCofT_EEV2yGGEvVdIpZB6PoXbzPHvqUzKHdiI7J-h4a9mpAiwCvD48; sgid=20-32111523-AVoWf7iaxPYrYS1bZPJgQt4Q; ad=YjpbSkllll2zxgQ1lllllVobZJolllllGU9xlkllllYlllllpZlll5@@@@@@@@@@; SUID=020141315D68860A59F9903400011F8A; PHPSESSID=6pguoaldhf1qrmgd5d593kt590; SUIR=9596D9A69792C89C1843AB2A98592145; SNUID=8B88C8BB8A8FD68FF63BCA508AAF1D6F; ppmdig=15120059080000001f53e33f6a5e54330a2700a58080fe0d; sct=19',
'Host':'weixin.sogou.com',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
}
proxy=None
ProxyCount=0
def get_html(url,count=1,timeout=5):
    print ('正在下载',url)
    print("正在请求第",count,"次")
    global proxy
    if count>=MAX_COUNT:
        print('请求次数太多')
        return  None
    try:
        if proxy:
            pro = ''.join(str(proxy).strip())

            proxies={
                'http':'http://'+proxy
            }
            response=requests.get(url,allow_redirects=False,timeout=timeout,headers=headers,proxies=proxies)

        else:
            response = requests.get(url, allow_redirects=False,timeout=timeout,headers=headers)
        print (response.status_code)
        if response.status_code==200:
            return response.text
        if response.status_code!=200:
            print(response.status_code)
            proxy=get_proxy()
            if proxy:
                print('正在使用代理:',proxy)
                #count+=1
                return get_html(url)
            else:
                print("获取代理失败！")
                return None

    except Exception as e:
        print('出错：',e.args)
        proxy=get_proxy()
        count+=1
        return get_html(url,count)
def get_proxy():
    global ProxyCount
    ProxyCount+=1;
    time.sleep(0)
    try:
        response=requests.get(PROXY_URL)
        if response.status_code==200:
            return response.text
        return None
    except ConnectionError:
        return None
def get_index(KEYWORD,PAGE):
    global index_url
    data={
        'query':KEYWORD,
        'type':2,
        'page':PAGE

    }
    queries=urlencode(data)
    url=base_url+queries
    index_url=url
    html=get_html(url)
    return html
def parse_index(html):
    doc=pq(html)
    items=doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')
def get_detail(url):
    try:
        response=requests.get(url)
        if response.status_code==200:
            return response.text
        return None
    except ConnectionError:
        return  None
def Parse_detail(html):
    try:
        doc=pq(html)
        title=doc('.rich_media_title').text()
        content=doc('.rich_media_content ').text()
        date=doc('#post-date').text()
        nickname=doc('#js_profile_qrcode > div > strong').text()
        wechat=doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        pattern=re.compile('<p.*?><img.*?data-src="(.*?)".*?/></p>',re.S)
        result=re.findall(pattern,html)
        image_urls =result
        #items=doc('.rich_media_content p').items()


        if image_urls:
            download_image(title,date,image_urls)

        return {
            'title':title,
            'content':content,
            'date':date,
            'nickname':nickname,
            'wechat':wechat,
            'image_urls':[url+"\n###\n" for url in image_urls]
        }
    except XMLSyntaxError:
        return  None
def download_image(title,date,urls):
    global index_url
    header={
    'authority': 'mmbiz.qpic.cn',
    'method': 'GET',
    'path': '/ mmbiz_jpg / X2VhfqvibrbZKtGlzCoIU5wicVI7oib6bptibo7Qeiace86S9lNRUf5TyR41aZa8DTolUOYkMqo6hGHpdZYMLXT2WXQ / 0?wx_fmt = jpeg',
    'scheme': 'https',
    'accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8',
    'accept - encoding': 'gzip, deflate, br',
    'accept - language': 'zh - CN, zh;q = 0.9',
    'cache - control': 'max - age = 0',
    'if -modified - since': 'Fri, 22 Sep 2017 17:13:44 GMT',
    'upgrade - insecure - requests': '1',
    'User - Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }
    for url in urls:
        try:
            url=url.replace("\'","")
            #print(url)
            response=requests.get(url,timeout=5,headers=header)
            #print(response.status_code)
            if response.status_code==200:
                print('正在下载图片。。。',title)
                save_image(title,date,response.content)
            if response.status_code!=200:
                print('图片下载失败！')
                return None
        except Exception:
            return None
def save_image(title,date,content):
    #file_path='{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    print('正在保存图片。。。',title)
    path=(str(title)+str(date)).replace("?", '_').replace("|","-").replace("/","").replace("\\","").replace("<","").replace(">","").replace("\"","").replace(":","").replace("*","")
    exist=os.path.exists(os.path.join("E:\Weixin",path))
    if not exist:
        os.makedirs(os.path.join("E:\Weixin",path))
    os.chdir(os.path.join("E:\Weixin",path))
    name=md5(content).hexdigest()+".jpg"
    f=open(name,'ab')
    f.write(content)
    f.close()

def save_to_mongo(data):
    if db['weixinmeinv'].update({'title':data['title'],'wechat':data['wechat']},{'$set':data},True):
        print('Save to Mongo',data['title'])
    else:
        print('Save to Mongo Failed',data['title'])
def main():
    for page in range(1,101):
        html=get_index(KEYWORD,page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html=get_detail(article_url)
                if article_html:
                    article_data=Parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)
if __name__=='__main__':
    main()
    print('共使用代理数为：',ProxyCount)
