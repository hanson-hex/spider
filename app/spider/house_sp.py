# /usr/bin/env python
#-*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json
import xlwt
from fake_useragent import UserAgent
import time
import random
import threading
from app.models.house import House
from app import db


infos = []
workbook = xlwt.Workbook()


def message_from_url(url, city, province):
    time.sleep(random.randint(0, 3))
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    response = requests.get(url, timeout=60, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    script = soup.select_one('script#sf-item-list-data')
    items = json.loads(re.sub(r'\s*', '', script.text))['data']
    sub_infos = []
    print(" come from %s" % threading.currentThread().getName())
    for item in items:
        info = {}
        info['province'] = province
        info['city'] = city
        info['target'] = item['title']

        info['currentPrice'] = str(item['currentPrice'])
        info['currentPrice'] = info['currentPrice'].split('.')[0]
        info['currentPrice'] = info['currentPrice'].strip()
        info['currentPrice'] = info['currentPrice'].replace(',', '')
        info['currentPrice'] = info['currentPrice'].split('.')[0]

        info['bidCount'] = int(item['bidCount'])
        info['marketPrice'] = item['consultPrice']
        if info['marketPrice'] == 0.0:
            info['marketPrice'] = str(item['marketPrice'])
            info['marketPrice'] = info['marketPrice'].strip()
            info['marketPrice'] = info['marketPrice'].replace(',', '')
            info['marketPrice'] = info['marketPrice'].split('.')[0]

        info['applyCount'] = int(item['applyCount'])
        info['viewerNum'] = int(item['viewerCount'])
        info['startTime'] = int(item['start'] / 1000)
        info['stopTime'] = int(item['end'] / 1000)
        if item['status'] == 'doing':
            info['status'] = '正在进行'
        elif item['status'] == 'done' or item['status'] == 'failure':
            info['status'] = '已经结束'
        elif item['status'] == 'break':
            info['status'] = '中止'
        elif item['status'] == 'revocation':
            info['status'] = '撤回'
        else:
            info['status'] = '即将开始'
        item_url = 'http:%s' % item['itemUrl']
        time.sleep(random.random())
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        response = requests.get(item_url, timeout=60, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        s_department = soup.select_one('div.pai-info > p:nth-of-type(2) > a')
        print('s_department', s_department)
        if s_department is None:
            i = soup.select_one('div.pai-info > p:nth-of-type(2)').text
            i = re.sub(r'\s*', '', i)
            info['department'] = i.split("：")[1]
        else:
            # page > div:nth-child(7) > div > div > div.pm-main-l.auction-interaction > div.pai-info > p:nth-child(2) > a
            info['department'] = soup.select('div.pai-info > p:nth-of-type(2) > a')[0].text
        # print(info['department'])

        info['startPrice'] = soup.select('span.J_Price')[0].text
        info['startPrice'] = info['startPrice'].strip()
        info['startPrice'] = info['startPrice'].replace(',', '')
        info['startPrice'] = info['startPrice'].split('.')[0]
        print(info['startPrice'])

        info['addPrice'] = soup.select('span.J_Price')[2].text
        info['addPrice'] = info['addPrice'].strip()
        info['addPrice'] = info['addPrice'].replace(',', '')

        info['deposit'] = soup.select('#J_HoverShow > tr:nth-of-type(2) > td:nth-of-type(1) > span.pai-save-price > span')[
                0].text
        info['deposit'] = str(info['deposit'])
        info['deposit'] = info['deposit'].strip()
        info['deposit'] = info['deposit'].replace(',', '')
        info['deposit'] = info['deposit'].split('.')[0]

        info['period'] = soup.select('#J_HoverShow > tr:nth-of-type(2) > td:nth-of-type(2) > span:nth-of-type(2)')[
            0].get_text()
        info['period'] = info['period'][1:]
        sub_infos.append(info)
        print('抓取到 %s' % item['title'])
    infos.extend(sub_infos)
    # print('infos', infos)


def save_sheet_in_excel():
    sheet = workbook.add_sheet('sheet')
    names = ['省份', '城市', '标的物', '当前价', '出价数', '评估价', '报名人数', '围观人数', '开拍时间',
             '预计结束时间', '状态', '处置单位', '起拍价', '加价幅度', '保证金', '竞价周期']
    for index, name in enumerate(names):
        sheet.write(0, index, name)

    for index, info in enumerate(infos):
        row = index + 1
        for key, value in info.items():
            index = names.index(key)
            sheet.write(row, index, value)
    # 设置冻结
    sheet.panes_frozen = True
    sheet.horz_split_pos = 1


def create_thread(pages, base_url, city, province):
    thread_list = []
    for index, page in enumerate(range(pages)):
        thread_name = "thread_%s" % index
        url = base_url + '&page=' + str(index)
        thread_list.append(threading.Thread(target=message_from_url, name=thread_name, args=(url, city, province)))
    return thread_list


def city_of_url(url, search_citys):
    url = 'http://%s' % url
    # print('url', url)
    print('search_citys', search_citys)
    # 构造请求数据
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    response = requests.get(url, timeout=60, headers=headers)
    # print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    tags = soup.select('ul > li.triggle.unfold > div > ul > li > em > a')
    # print(tags)
    sub_urls = []
    citys = []
    for tag in tags:
        u = tag['href']
        city = tag.text
        # print('city', city)
        citys.append(city)
        url = u.split('//')[1]
        # print('url', url)
        sub_urls.append(url)
    search_urls = []
    # 选择符合要求的城市
    for index, city in enumerate(citys):
        if city in search_citys:
            search_urls.append(sub_urls[index])
    print(search_urls)
    return search_urls


def province_of_url(url):  # pai-item-560704665191 > a > div.footer-section > p.num-auction
    response = requests.get(url)
    # print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    tags = soup.select('ul > li > em > a')
    # print(tags)
    urls = []
    provinces = []
    search_provinces = dict(
        安徽=['合肥'],
        甘肃=['兰州'],
        广西=['南宁'],
        贵州=['贵阳'],
        海南=['海口', '三亚'],
        河北=['石家庄'],
        黑龙江=['哈尔滨'],
        吉林=['长春'],
        江苏=['徐州', '无锡', '常州', '南京', '南通'],
        江西=['南昌'],
        辽宁=['大连', '沈阳'],
        山东=['济南', '青岛'],
        山西=['太原'],
        陕西=['西安'],
        新疆=['乌鲁木齐'],
        云南=['昆明'],
        浙江=['温州', '宁波', '绍兴', '嘉兴', '金华', '台州'],
        北京=['北京'],
        上海=['上海'],
        重庆=['重庆'],
        天津=['天津'],
        广东=['中山', '广州', '深圳', '东莞', '惠州', '珠海']
    )
    tags = tags[11:43]
    web_province = ['浙江', '江苏', '河南', '福建', '上海', '广东', '安徽', '内蒙古', '北京', '湖北', '云南', '山东', '海南', '江西', '广西', '天津',
                    '重庆', '湖南', '河北', '四川', '山西', '贵州', '宁夏', '青海', '辽宁', '吉林', '黑龙江', '西藏', '陕西', '甘肃', '新疆', '香港']
    print('tags', tags)
    for tag in tags:
        u = tag['href']
        province = tag.text
        print('provice', province)
        provinces.append(province)
        url = u.split('//')[1]
        print('url', url)
        urls.append(url)
    print('打印所有urls', urls)
    p_urls = {}
    sp = list(search_provinces.keys())
    print('sp', sp)
    print('浙江' in sp)
    for index, province in enumerate(web_province):
        print('province', province)
        if province in sp:
            print('选择出url')
            p_urls[province] = urls[index]
    print('目标爬取省份字典%s' % p_urls)
    return p_urls, search_provinces


def clear_infos():
    global infos
    infos = []


def save_data_in_database():
    db.drop_all()
    db.create_all()
    print(len(infos))
    for info in infos:
        house = House(info)
        house.save()


def spider_house():
    base_url = 'https://sf.taobao.com/item_list.htm?spm=a213w.7398504.filter.2.GytMAm&category=50025969&auction_start_seg=0&auction_start_from=2017-10-01&auction_start_to=null'
    provinces_urls, provinces = province_of_url(base_url)
    for province, p_url in provinces_urls.items():
        citys = provinces[province]
        print(citys)
        urls = city_of_url(p_url, citys)
        # 历遍城市url
        for index, url in enumerate(urls):
            url = 'http://%s' % url
            ua = UserAgent()
            headers = {'User-Agent': ua.random}
            response = requests.get(url, timeout=60, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            print('爬取 %s 市' % citys[index])
            total_page = int(soup.select_one('em.page-total').text)
            print('一共 %s 页数据' % total_page)
            # 创建线程
            thread_list = create_thread(total_page, url, citys[index], province)
            # 启动所有线程
            for thread in thread_list:
                thread.start()
            # 主线程中等待所有子线程退出
            for thread in thread_list:
                thread.join()
    # 保存到数据库里面
    save_data_in_database()


def test():
    city = '乌鲁木齐'
    province = '新疆'
    url = 'https://sf.taobao.com/item_list.htm?spm=a213w.7398504.filter.47.XY422R&category=50025969&city=%CE%DA%C2%B3%C4%BE%C6%EB&province=&auction_start_seg=-1'
    message_from_url(url, city, province)
    print(infos)
    save_data_in_database()


if __name__ == '__main__':
    spider_house()
    # test()
    # db.drop_all()

