# -*- coding: utf-8 -*-
# @Time    : 2023/3/18 22:38
# @Author  : muyangren907
# @Email   : myr907097904@gmail.com
# @File    : WeiboOnedrive.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
# @Time    : 2021/7/18 16:39
# @Author  : muyangren907
# @Email   : myr907097904@gmail.com
# @File    : WeiboTGup.py
# @Software: PyCharm
import datetime
import logging
import os
import re
import shutil
import sqlite3
import time
import traceback

import requests
# 第一步，创建一个logger
import urllib3

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级开关
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
urllib3.disable_warnings()


def sleep_dis(sleep_time):
    for i in range(sleep_time, -1, -1):
        print('休眠 %5s s' % i, end='\r')
        time.sleep(1)


def dd2sttime(dd):
    # dd = "Fri Nov 09 2018 14:41:35 GMT+0800 (CST)"

    # dd = 'Tue Mar 08 16:48:11 +0800 2022'
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    return datetime.datetime.strptime(dd, GMT_FORMAT).strftime('%Y_%m_%d_%H_%M_%S')
    # print()


def get_database_conn():
    conn = sqlite3.connect('Weibo.db')
    return conn


def insert_db(author_id, author_nickname, video_id, video_title, video_url):
    conn = get_database_conn()
    cursor = conn.cursor()
    sql = 'INSERT OR IGNORE INTO "main"."WeiboVideos"("author_id", "author_nickname", "video_id", "video_title", "video_url") VALUES ("{}", "{}", "{}", "{}", "{}")'.format(
        author_id, author_nickname, video_id, video_title, video_url)

    cursor.execute(sql)
    # # 关闭Cursor:
    cursor.close()
    # 提交事务:
    conn.commit()
    # 关闭Connection:
    conn.close()


def get_downloaded_from_db(author_id):
    conn = get_database_conn()
    cursor = conn.cursor()
    # type_, nickname_ = get_type_and_nickname()
    sql = 'SELECT * FROM WeiboVideos WHERE author_id="{}"'.format(author_id)
    cursor.execute(sql)
    values = cursor.fetchall()
    vks = [vk[2] for vk in values]
    # # 关闭Cursor:
    cursor.close()
    # 提交事务:
    conn.commit()
    # 关闭Connection:
    conn.close()
    return vks


# 字符格式化
def strfomat(str_in):
    sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", str_in)
    return sub_str


def getconfini():
    users_ = {}
    weiboinitxt = ''
    with open('Weibo.ini', encoding='utf-8', mode='r') as weiboini:
        weiboinitxt = weiboini.read()

    lines = [line for line in weiboinitxt.split('\n') if line != '']
    users_ids_ = []
    for line in lines:
        id_, nickname_ = line.split('#')
        id_ = id_.replace('oid = ', '').replace("'", '').replace(" ", '')
        # nickname_ = strfomat(nickname_)
        nickname_ = nickname_.strip()
        # print('{},-1001569385968'.format(nickname_))
        nickname_ini = nickname_
        users_[id_] = nickname_ini
        users_ids_.append(id_)
    return users_,users_ids_


headers = {
    "Connection": "keep-alive",
    "User-Agent": "Weibo/41997 (iPhone; iOS 13.3.1; Scale/3.00)",
    "X-Validator": "m30ICw/HjsotVLZThjoyUr0x04+Mx/h19DOfG+oQspU=",
    "X-Sessionid": "C028AA66-F84F-4E1E-8F43-5A7BEF8E7167",
    "X-Log-Uid": "5155102894",
    "cronet_rid": "6554986",
    "SNRT": "normal",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",

}


def get_cardlist(fid, since_id):
    # url = 'https://api.weibo.cn/2/cardlist?gsid=_2A25zfYxTDeRxGeNP7lcQ8CzEwjiIHXVuKpibrDV6PUJbi9AKLU7SkWpNTmi7Fm6HA7BcVndj1N0FJPKE-NxENVTx&from=10A3293010&c=iphone&s=dd7af2c0&containerid={}&fid={}'.format(
    #     fid, fid)
    url = 'https://api.weibo.cn/2/cardlist?c=iphone&s=c9ad28e8&gsid=_2AkMqvgPef8NhqwJRmPEXyG7nbIR2yQ3EieKc4vIFJRM3HRl-wT92qkAMtRV6BtnEpqNYjBzy3qjqLqjaekw667WNcZdy&from=10A3293010&containerid={}'.format(
        fid)
    if since_id != '0':
        url = '{}&since_id={}'.format(url, since_id)
    # print(url)
    while True:
        try:
            res = requests.get(url, headers=headers)
            if debug_mode:
                logger.info('{}'.format(res.text))
            resjson = res.json()
            break
        except Exception as e:
            # print(e)

            traceback.print_exc()
            time.sleep(2)
    # print(res.text)
    return resjson


def get_containerid(oid):
    global errors_
    # url ='https://api.weibo.cn/2/profile?from=10A3293010&user_domain=6802638701'
    url = 'https://api.weibo.cn/2/profile?from=10A7093022&c=iphone&s=a6d2591f&user_domain={}'.format(oid)
    headers = {
        'authority': 'api.weibo.cn',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    params = (
        ('from', '10A7093022'),
        ('c', 'iphone'),
        ('s', 'a6d2591f'),
        ('user_domain', '{}'.format(oid)),
    )

    # params = (
    #     ('user_domain', '{}'.format(oid)),
    # )

    res = requests.get('https://api.weibo.cn/2/profile', headers=headers, params=params)
    # print(res.headers)
    if debug_mode:
        logger.info(url)
    # print(url)
    # res = requests.get(url, headers=headers)
    if debug_mode:
        print(res.text)
    try:
        resjson = res.json()
        userInfo = resjson['userInfo']
        name = userInfo['name']
        tabs = resjson['tabsInfo']['tabs']
        containerid = ''
        for tab in tabs:
            if tab['title'] == '相册':
                containerid = tab['containerid']
                break
    except:
        traceback.print_exc()
        logger.info(res.text)
        errors_[oid] = res.text
        return -1, -1
        # exit(0)
    return containerid, name


# 下载主模块
def download_(d_url, d_cap, d_type):
    hz = ''
    if d_type == 'video':
        down_path = os.path.join(author_path, '视频')
        if '.mp4' in d_url:
            hz = '.mp4'
        elif '.mov' in d_url:
            hz = '.mov'
        else:
            hz = '.mp4'
    elif d_type == 'pic':
        down_path = os.path.join(author_path, '图片')
        if '.jpg' in d_url:
            hz = '.jpg'
        elif '.gif' in d_url:
            hz = '.gif'
        elif '.png' in d_url:
            hz = '.png'
        else:
            hz = '.png'

    if not os.path.exists(down_path):
        os.makedirs(down_path)

    # base_name = os.path.basename(d_url)

    # hz = d_url.split('.')[-1].split('?')[0]
    # d_cap = '{}{}'.format(d_cap, hz)

    f_name = '微博_{}_{}_{}_{}{}'.format(nickname_ini_, name, oid, d_cap, hz)

    # if not os.path.exists(os.path.join(down_path, d_cap)) and d_cap not in have_down_list:
    if d_cap in have_down_list:
        logger.info('已经下载 {}'.format(f_name))
    else:
        if not os.path.exists(os.path.join(down_path, f_name)):
            # print('[%04d / %04d]正在加入 %s' % (i + 1, photo_lists_len, down_title))
            logger.info('正在加入 {}'.format(f_name))

            d_cmd = 'aria2c --file-allocation=none -x 16 -s 16 -k 1M --disable-ipv6 -o "{}" "{}"'.format(f_name,
                                                                                                         d_url)
            logger.info('{}'.format(d_cmd))
            if not debug_mode:
                os.system(d_cmd)
            # f_name = d_cap
            author_id = oid
            author = nickname_ini_
            video_id = d_cap
            video_url = d_url
            if debug_mode:
                logger.info('insert_db({},{},{},{},{})'.format(author_id, author, video_id, f_name, video_url))
                sql = 'INSERT OR IGNORE INTO "main"."WeiboVideos"("author_id", "author_nickname", "video_id", "video_title", "video_url") VALUES ("{}", "{}", "{}", "{}", "{}")'.format(
                    author_id, author, video_id, f_name, video_url)
                logger.info('{}'.format(sql))
            if not debug_mode:
                record_ok_path = os.path.join(root_path,nickname_ini_)
                if not os.path.exists(record_ok_path):
                    os.makedirs(record_ok_path)
                if not os.path.exists(os.path.join(record_ok_path, f_name)):
                    if os.path.exists(f_name):
                        shutil.move(f_name, record_ok_path)
                    else:
                        logger.error('未下载完成{}'.format(f_name))
                        notdlist.append(f_name)
            if os.path.exists(os.path.join(record_ok_path, f_name)):
                logger.info('insert_db({},{},{},{},{})'.format(author_id, author, video_id, f_name, video_url))
                try:
                    insert_db(author_id, author, video_id, f_name, video_url)
                except Exception as e:
                    traceback.print_exc()
            # call([idmPath, '/d', d_url, '/p', down_path, '/f', d_cap, '/n', '/a'])
            # have_down_list.append(d_cap)
        else:
            logger.info('文件已存在 {}'.format(f_name))


def deal_json(cardlist):
    # print(cardlist)
    cardlistInfo = cardlist['cardlistInfo']
    cards = cardlist['cards']
    since_id = ''
    # print(since_id)
    if 'since_id' in cardlistInfo:
        since_id = cardlistInfo['since_id']
        logger.info('since_id {}'.format(since_id))
    else:
        logger.warning("'since_id' not in cardlistInfo")
    # print(since_id)
    try:
        for card in cards:
            card_type_name = card['card_type_name']
            if card_type_name == '组合':
                card_groups = card['card_group']
                for card_group in card_groups:
                    pics = card_group['pics']

                    for pic in pics:
                        # d_urls = []
                        # d_caps = []
                        mblog = pic['mblog']
                        mid = mblog['mid']
                        created_at = mblog['created_at']
                        created_at = dd2sttime(created_at)
                        pic_id = ''
                        if debug_mode:
                            logger.info(pic)

                        if 'pic_id' in pic:
                            pic_id = pic['pic_id']
                        if 'video' in pic:
                            d_url = pic['video']
                            d_cap = '{}_{}_{}'.format(created_at, mid, pic_id)
                            download_(d_url, d_cap, 'video')
                        if 'pic_mw2000' in pic:
                            d_url = pic['pic_mw2000']
                            d_cap = '{}_{}_{}'.format(created_at, mid, pic_id)
                            download_(d_url, d_cap, 'pic')
                        elif 'pic_big' in pic:
                            d_url = pic['pic_big']
                            d_cap = '{}_{}_{}'.format(created_at, mid, pic_id)
                            download_(d_url, d_cap, 'pic')

                        if 'page_info' in mblog and mblog['page_info'] != '':
                            # 视频
                            # continue
                            page_info = mblog['page_info']
                            logger.info(page_info)
                            # print(mblog)
                            page_id = page_info['page_id']
                            object_type = page_info['object_type']
                            if 'media_info' not in page_info:
                                print(page_info)
                                logger.error(page_info)
                                sleep_dis(10)
                                continue
                            media_info = page_info['media_info']
                            if 'mp4_hd_url' in media_info:
                                d_url = media_info['mp4_hd_url']
                            elif 'mp4_sd_url' in media_info:
                                d_url = media_info['mp4_sd_url']
                            else:
                                logger.warning('视频链接出错')

                            # d_cap = '{}_{}'.format(mid, page_id)
                            d_cap = '{}_{}_{}'.format(created_at, mid, pic_id)
                            download_(d_url, d_cap, 'video')

                            # print(d_cap)
                            # print(d_url)
                            # video_list.append(mp4_hd_url)

                        # print(mblog)
                        # mblogtype = mblog['mblogtype']
                        # print('mblogtype {}'.format(mblogtype))

                        # if 'type' in pic:
                        #     type = pic['type']
                        #     print(type)
                        #     if type == 'livephoto':
                        #         # livephoto
                        #
                        #         pic_id = pic['pic_id']
                        #         d_url = pic['video']
                        #         d_cap = '{}_{}'.format(mid, pic_id)
                        #         download_(d_url, d_cap, 'video')
                        #
                        #         d_url = pic['pic_big']
                        #
                        #         d_cap = '{}_{}'.format(mid, pic_id)
                        #         download_(d_url, d_cap, 'pic')
                        #     else:
                        #         print(pic)
                        #         print(type)
                        #         print('类型未知')
                        # elif 'page_info' in mblog:
                        #     # 视频
                        #     continue
                        #     page_info = mblog['page_info']
                        #     print(mblog)
                        #     page_id = page_info['page_id']
                        #     object_type = page_info['object_type']
                        #     media_info = page_info['media_info']
                        #     if 'mp4_hd_url' in media_info:
                        #         d_url = media_info['mp4_hd_url']
                        #     elif 'mp4_sd_url' in media_info:
                        #         d_url = media_info['mp4_sd_url']
                        #     else:
                        #         print('视频链接出错')
                        #
                        #     d_cap = '{}_{}'.format(mid, page_id)
                        #
                        #     download_(d_url, d_cap, 'video')
                        #
                        #     # print(d_cap)
                        #     # print(d_url)
                        #     # video_list.append(mp4_hd_url)
                        # else:
                        #     # 非视频 和 live_photo
                        #     pic_id = pic['pic_id']
                        #     d_url = pic['pic_big']
                        #
                        #     d_cap = '{}_{}'.format(mid, pic_id)
                        #     download_(d_url, d_cap, 'pic')
                        #     # pass
            else:
                logger.info(card_type_name)
    except Exception as e:
        traceback.print_exc()
        return 0
    return since_id


def get_have_down_list(author_path):
    have_down_list = []
    have_down_txt = os.path.join(author_path, 'have_down.txt')
    if not os.path.exists(have_down_txt):
        with open(have_down_txt, 'w', encoding='utf8') as hdtxt:
            pass
        return have_down_list
    with open(have_down_txt, 'r', encoding='utf8') as hdtxt:
        have_down_text = hdtxt.read()

    have_down_list = [hd for hd in have_down_text.split('\n') if hd != '']
    return have_down_list


def writeback_have_down_list(author_path):
    have_down_txt = os.path.join(author_path, 'have_down.txt')
    with open(have_down_txt, 'w', encoding='utf8') as hdtxt:
        for have_down in have_down_list:
            hdtxt.write('{}\n'.format(have_down))


def dis_errors():
    for oid in errors_:
        logger.info('{} {}'.format(oid, errors_[oid]))


if __name__ == '__main__':
    debug_mode = False
    errors_ = {}
    users_ini,users_ids_ini = getconfini()
    logger.info(users_ini)
    record_ok_path = r'F:\video\weibo'
    TRY_MAX = 5

    root_path = r'F:\video\weibo'
    oididx = 0
    for oid in users_ids_ini:
        notdlist = []
        oididx += 1
        print()
        logger.warning('{}'.format('=' * 30))
        nickname_ini_ = users_ini[oid]
        logger.info('开始获取[{} / {}] {} {}'.format(oididx, len(users_ini), oid, nickname_ini_))
        containerid, name = get_containerid(oid)
        if containerid == -1:
            logger.error('{} {} 错误 跳过，休息5s'.format(oid, nickname_ini_))
            sleep_dis(5)
            continue

        logger.info('{} {} {}'.format(name, oid, containerid))
        # containerid = '2318267240907089'

        # author_path = os.path.join(root_path, oid)
        author_path = root_path
        if not os.path.exists(author_path):
            os.makedirs(author_path)

        # have_down_list = get_have_down_list(author_path)
        have_down_list = get_downloaded_from_db(oid)

        logger.info('{}'.format(have_down_list))
        logger.info('{} {} 已经下载项目 {} 个'.format(nickname_ini_, oid, len(have_down_list)))
        sleep_dis(2)

        since_id = 1
        page_idx = 0
        video_list = []

        since_idtmp = 0
        while since_id != 0:
            # while since_id != 0 and since_idtmp - page_idx < 1:
            page_idx += 1
            logger.info('正在处理第 {} 页'.format(page_idx))
            sleep_dis(5)
            cardlist = get_cardlist(containerid, since_id)
            if 'cardlistInfo' not in cardlist:
                logger.error('{} {} 错误 cardlistInfo not in cardlist，休息5s'.format(oid, nickname_ini_))
                sleep_dis(5)
                break
            # print('cardlist', cardlist)
            try_time = 0
            while try_time < TRY_MAX:
                try_time += 1
                try:
                    since_id = deal_json(cardlist)
                    logger.info('since_id in try {}'.format(since_id))
                    break
                except Exception as e:
                    traceback.print_exc()
                    # print('Exception in')
                    # print(e)
                    # print('sleep 10 s')
                    time.sleep(10)
                    # exit(907)
            logger.info('{} {}'.format(since_id, since_idtmp))
            if since_id != 0:

                # since_idtmp = int(since_id.split('kp')[-1])
                since_idtmp = since_id
            else:
                since_idtmp = since_id
            logger.info('{} {}'.format(since_idtmp, page_idx))
            # print(since_id)
            # call([idmPath, '/s'])
            sleep_dis(5)
        logger.error('该作者未完成下载')
        for iiiii in notdlist:
            print('{}'.format(iiiii))
        # writeback_have_down_list(author_path)
        logger.info('处理完一个，休息5s')
        sleep_dis(5)

    dis_errors()
