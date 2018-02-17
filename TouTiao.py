import json
import re
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing import Pool
import os
import pymongo
from TouTiao_config import *
import requests
from bs4 import BeautifulSoup
# from json.decoder import JSONDecodeError

client = pymongo.MongoClient(MONGO_URL, connect=False)     #声明一个mongodb对象并传入MONGO_URL
db = client[MONGO_DB]   #传入数据库名称

def get_page_index(offset, keyword):
    '''索引页的数据是json格式，所以在解析索引页时需要json库加载'''
    data = {
        'offset': 0,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
        print('请求索引页出错')
        return None

def parse_page_index(html):
    '''索引页负责拿到详情页的url'''
    #try:
    data = json.loads(html)     #json数据就是键值对
    if data and 'data' in data.keys():
        for item in data.get('data'):
            # print(item)
            yield item.get('article_url')
    # except JSONDecodeError:
    #     pass

def get_page_detail(url):
    '''把从索引页得到的详情页url打开，获取详情页html'''
    try:
        header = {'User-Agent':'my-app/0.0.1'}
        response = requests.get(url, headers=header)        #详情页的地址反爬虫了 -.-
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
        print('请求详情页出错', url)
        return None

def parse_page_detail(html, url):
    '''图片是在原始的html，所以用requests可以获取html'''
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    print(title)

    images_pattern = re.compile('gallery: JSON.parse\("(.*?)"\),', re.S)    #因为json是以分号结尾的，所以加个分号
    result = re.search(images_pattern, html)
    temp = result.group(1)
    temp1 = re.sub('\\\\', '', temp)

    if temp1:
        data = json.loads(temp1)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]        #列表推导式返回的是列表
            for image in images:
                download_images(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }
        # print(result.group(1))

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功', result)
        return True
    return False

def download_images(url):
    print('正在下载', url)
    try:
        header = {'User-Agent':'my-app/0.0.1'}
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            save_image(response.content)    #response.content-保存图片的二进制数据
        return None
    except requests.RequestException:
        print('请求图片出错', url)
        return None

def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)

def main(offset):
    html = get_page_index(offset, KEYWORD)
    for url in parse_page_index(html):
        '''用索引页的html把详情页的article_url'''
        html = get_page_detail(url)
        if html.find('gallery: JSON.parse') > 0:
            result = parse_page_detail(html, url)
            if result: save_to_mongo(result)
            print(result)
            print('-----------------------------------------这个链接可提取图片！-----------------------------------------')

if __name__ == '__main__':
    # main()
    groups = [x*20 for x in range(GROUP_START, GROUP_END + 1)]
    pool = Pool()
    pool.map(main, groups)