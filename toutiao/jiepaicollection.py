# -*- coding: utf-8  
import requests
import os
from hashlib import md5
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup
from config import *
import pymongo
import os
from json.decoder import JSONDecodeError
from multiprocessing import Pool
client=pymongo.MongoClient(MONGO_URL,connect=False)
db=client[MONGO_DB]
import re
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
def get_page_index(offest,keyword):
    
    data={
        'offset':offest,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':20,
        'cur_tab':3
        }
    url='https://www.toutiao.com/search_content/?'+urlencode(data)
    headers['Referer']=url;
    try:
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错')
        return None
def parse_page_index(html):
    try:
        data=json.loads(html);
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        pass
def get_page_detail(url):
     try:
        headers['Referer']=url;
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            return response.text
        return None
     except RequestException:
         print('请求详情页出错',url)
         return None
def parse_page_detail(html,url):
     soup=BeautifulSoup(html,'lxml')
     title=soup.select('title')[0].get_text()
     print(title)
     images_pattern=re.compile('JSON.parse\("(.*?)"\)',re.S)
     result=re.search(images_pattern,html)
     
     if result:
        # print(result.group(1))
         data=json.loads(result.group(1).replace('\\',''))
         if data and 'sub_images' in data.keys():
             sub_images=data.get('sub_images')
             images=[item.get('url') for item in sub_images]
             for image in images:
                 download_image(image,title)
             return{
                 'title':title,
                 'url':url,
                 'image':images
                 }
def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功',result)
        return True
    return False
def download_image(url,title):
     print('正在下载',url)
     try:
        headers['Referer']=url;
        response=requests.get(url,headers=headers)
        if response.status_code==200:
           save_image(response.content,title)
        return None
     except RequestException:
         print('请求图片出错',url)
         return None
def save_image(content,title):
    path=str(title).strip()
    isExists=os.path.exists(os.path.join(os.getcwd(),path))
    if not isExists:
        os.makedirs(os.path.join(os.getcwd(),path))
    file_path='{0}/{1}.{2}'.format(os.path.join(os.getcwd(),path),md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()
def main(offset):
    html_index=get_page_index(offset,KEYWORD)
    for url in parse_page_index(html_index):
        html=get_page_detail(url)
        if html:
           result= parse_page_detail(html,url)
           if result:
               save_to_mongo(result)
if __name__=='__main__':
    groups=[x*20 for x in range(GROUP_START,GROUP_END+1)]
    pool=Pool()
    pool.map(main,groups)
