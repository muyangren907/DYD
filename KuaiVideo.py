# -*- coding: utf-8 -*-
# @Time    : 2022/2/1 2:20
# @Author  : muyangren907
# @Email   : myr907097904@gmail.com
# @File    : KwaiVideos.py
# @Software: PyCharm
# coding:utf-8
import datetime
import logging  # 引入logging模块
import os
import random
import re
import shutil
import sqlite3
import threading
import time
import traceback

import requests
import urllib3
from KwaiUtils import KwaiUtils
from concurrent.futures import ThreadPoolExecutor

LOCK = threading.Lock()
# from zhon.hanzi import punctuation

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级开关
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

urllib3.disable_warnings()

def shuaxin(headers,cookies):
    # cookies = {
    #     'kpf': 'PC_WEB',
    #     'clientid': '3',
    #     'did': 'web_47f789445488c08089d2a468d7626e63',
    #     'didv': '1708888687000',
    #     'kpn': 'KUAISHOU_VISION',
    # }
    #
    # headers = {
    #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    #     'Connection': 'keep-alive',
    #     # 'Cookie': 'kpf=PC_WEB; clientid=3; did=web_47f789445488c08089d2a468d7626e63; didv=1708888687000; kpn=KUAISHOU_VISION',
    #     'DNT': '1',
    #     'Origin': 'https://www.kuaishou.com',
    #     'Referer': 'https://www.kuaishou.com/brilliant',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    #     'accept': '*/*',
    #     'content-type': 'application/json',
    #     'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    # }

    json_data = {
        'operationName': 'hotVideoQuery',
        'variables': {
            'trendingId': '习近平的两会妙喻',
            'page': 'brilliant',
            'webPageArea': 'brilliantxxunknown',
            'photoIds': [
                '3xdsrj544aisjk6',
            ],
        },
        'query': 'fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nquery hotVideoQuery($trendingId: String, $page: String, $webPageArea: String, $photoIds: [String]) {\n  hotVideoData(trendingId: $trendingId, page: $page, webPageArea: $webPageArea, photoIds: $photoIds) {\n    result\n    llsid\n    expTag\n    serverExpTag\n    pcursor\n    webPageArea\n    trendingId\n    feeds {\n      type\n      trendingId\n      author {\n        id\n        name\n        headerUrl\n        following\n        headerUrls {\n          url\n          __typename\n        }\n        __typename\n      }\n      photo {\n        ...photoContent\n        __typename\n      }\n      canAddComment\n      llsid\n      status\n      currentPcursor\n      __typename\n    }\n    __typename\n  }\n}\n',
    }
    response = requests.post('https://www.kuaishou.com/graphql', cookies=cookies, headers=headers, json=json_data)

def strfomat(str_in):
    sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", str_in)
    return sub_str


def sleep_dis(sleep_time):
    for i in range(sleep_time, -1, -1):
        print('休眠 %5s s' % i, end='\r')
        time.sleep(1)


def requestplus(req_type, req_url, req_headers={}, req_cookies={}, req_data=None, req_proxies={}, req_json={}):
    logger.info('{} {} {} {} {} {}'.format(req_type, req_url, req_headers, req_cookies, req_data, req_proxies))
    try_max = 20
    try_time = 1
    # req_cookies['did'] = kwaiutils.gen_did()
    while True:
        try_time += 1
        try:
            if req_type == 'get':
                res = requests.get(req_url, headers=req_headers, cookies=req_cookies, proxies=req_proxies,
                                   timeout=10)
            elif req_type == 'post':
                res = requests.post(req_url, headers=req_headers, cookies=req_cookies, proxies=req_proxies,
                                    data=req_data, json=req_json, timeout=10)
            break
        except Exception as e:
            traceback.print_exc()
            sleep_dis(5)
            if try_time == try_max:
                return -1
    return res


def get_database_conn():
    conn = sqlite3.connect('Kwaivideos.db')
    return conn


def logiprint(strin):
    logger.info('{}'.format(strin))


def getUa(pcOrMobile: int = 0):
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        ['(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
         '(Macintosh; Intel Mac OS X 10_12_6)'],
        [
            '(Linux; Android 6.0; Nexus 5 Build/MRA58N)', '(iPhone; CPU iPhone OS 15_1 like Mac OS X)',
            '(Linux; Android 11; V2049A Build/RP1A.200720.012; wv)',
            '(Linux; Android 10; HarmonyOS; MRX-AL09; HMSCore 6.3.0.327)',
            '(Linux; U; Android 9; zh-Hans-CN; HWI-AL00 Build/HUAWEIHWI-AL00)']]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)
    ua = ' '.join(['Mozilla/5.0', random.choice(os_type[pcOrMobile]), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Mobile Safari/537.36' if pcOrMobile else 'Safari/537.36'])
    return ua


def getCookies():
    _checkUrl = 'https://www.kuaishou.com/?utm_source=aa&utm_medium=05&utm_campaign=aa_05_pp_yr&plan_id=138090084&unit_id=5205658029&creative_id=43661481717&keyword_id=202928513388&keyword=202928513388&bd_vid=8380158842241119439'
    while True:
        try:
            logger.info('获取cookies')
            # r = requests.get((_checkUrl), headers={'User-Agent': getUa()})
            r = requests.get((_checkUrl), headers={'User-Agent': ua})
            cookies_ = r.cookies.get_dict()
            cookies = {
                'clientid': '3',
                'client_key': '65890b29',
                'did': 'web_2077198417aebfbbc48949437bff73f5',
                'did': '{}'.format(cookies_.get('did')),
                # 'didv': '1631014124364',
                'userId': '904333985',
                'kpf': 'PC_WEB',
                'kpn': 'KUAISHOU_VISION',
                # 'kuaishou.server.web_st': 'ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABsFMU0aBUpGBuTSUBUimcvEq1YQhbfYe0mY7gP5UBFphKHn6ztVRovH2uv7d9yKCaoX1y3zlO2JirGXPp4hoTbw8nEBt-tNu7Q-6j7bsC8mbzFVRKrWwS_9eGdzfOQlsw8cQPaf9jPUdEPFH0e-B2Jcctq8kjy7lG-Q0ds-vkgmC66-apE_c17gB25H3dSx8bmQp39-IpOLOON8Jk-OXRqhoSsguEA2pmac6i3oLJsA9rNwKEIiDDZaay9s3raetnSB81p_D69Knp-Hs2KP-KfXr0tALqZCgFMAE',
                # 'kuaishou.server.web_ph': 'cdb6a31bcf80dc19b9a26a853ea4de3fd5d8',
            }
            logger.info('获取到cookies {}'.format(cookies))
            break
        except Exception as e:
            traceback.print_exc()
            sleep_dis(2)

    return cookies


def getDid() -> str:
    _checkUrl = 'https://www.kuaishou.com/?utm_source=aa&utm_medium=05&utm_campaign=aa_05_pp_yr&plan_id=138090084&unit_id=5205658029&creative_id=43661481717&keyword_id=202928513388&keyword=202928513388&bd_vid=8380158842241119439'
    r = requests.get((_checkUrl), headers={'User-Agent': getUa()})
    did = r.cookies.get_dict().get('did')

    return did


def insert_db(author_id, author_nickname, video_id, video_title, video_url):
    LOCK.acquire()
    conn = get_database_conn()
    cursor = conn.cursor()
    sql = 'INSERT OR IGNORE INTO "main"."KwaiVideos"("author_id", "author_nickname", "video_id", "video_title", "video_url") VALUES ("{}", "{}", "{}", "{}", "{}")'.format(
        author_id, author_nickname, video_id, video_title, video_url)

    cursor.execute(sql)
    # # 关闭Cursor:
    cursor.close()
    # 提交事务:
    conn.commit()
    # 关闭Connection:
    conn.close()
    LOCK.release()


def get_downloaded_from_db(author_id):
    conn = get_database_conn()
    cursor = conn.cursor()
    # type_, nickname_ = get_type_and_nickname()
    sql = 'SELECT * FROM KwaiVideos WHERE author_id="{}"'.format(author_id)
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


def timestamp2strtime(timestamp):
    """将 13 位整数的毫秒时间戳转化成本地普通时间 (字符串格式)
    :param timestamp: 13 位整数的毫秒时间戳 (1456402864242)
    :return: 返回字符串格式 {str}'2016-02-25 20:21:04.242000'
    """
    local_str_time = datetime.datetime.fromtimestamp(timestamp / 1000.0).strftime('%Y_%m_%d_%H_%M_%S')
    return local_str_time


# 请求网页
def req_data(id, pcursor):
    # 请求头
    cookiess = []
    headerss = []

    '''
    json_data = {
        'operationName': 'visionProfilePhotoList',
        'variables': {
            'userId': '3x5mcxa5hc8wx7e',
            'pcursor': '1.675935110061E12',
            'page': 'profile',
        },
        'query': 'fragment photoContent on PhotoEntity {\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  __typename\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n',
    }

    '''
    json_data = {
        'operationName': 'visionProfilePhotoList',
        'variables': {
            'userId': '{}'.format(id),
            'pcursor': '{}'.format(pcursor),
            'page': 'profile',
        },
        # 'query': 'fragment photoContent on PhotoEntity {\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  __typename\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n',
        'query': 'fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n}\n\nfragment recoPhotoFragment on recoPhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    ...recoPhotoFragment\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n',

        # 'query': 'query visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      type\n      author {\n        id\n        name\n        following\n        headerUrl\n        headerUrls {\n          cdn\n          url\n          __typename\n        }\n        __typename\n      }\n      tags {\n        type\n        name\n        __typename\n      }\n      photo {\n        id\n        duration\n        caption\n        likeCount\n        realLikeCount\n        coverUrl\n        coverUrls {\n          cdn\n          url\n          __typename\n        }\n        photoUrls {\n          cdn\n          url\n          __typename\n        }\n        photoUrl\n        liked\n        timestamp\n        expTag\n        animatedCoverUrl\n        stereoType\n        videoRatio\n        profileUserTopPhoto\n        __typename\n      }\n      canAddComment\n      currentPcursor\n      llsid\n      status\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n',
    }
    req_headers['Referer'] = 'https://www.kuaishou.com/profile/{}'.format(id)
    # req_headers['Referer'] = 'https://www.kuaishou.com/brilliant'
    # req_cookies['did'] = kwaiutils.gen_did()
    cookiess.append(req_cookies)
    headerss.append(req_headers)
    if debugMode:
        logger.info('{} {}'.format(id, pcursor))
    # data = '{"operationName":"visionProfilePhotoList","variables":{"userId":"' + id + '","pcursor":"' + pcursor + '","page":"profile"},"query":"query visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\\n    result\\n    llsid\\n    webPageArea\\n    feeds {\\n      type\\n      author {\\n        id\\n        name\\n        following\\n        headerUrl\\n        headerUrls {\\n          cdn\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      tags {\\n        type\\n        name\\n        __typename\\n      }\\n      photo {\\n        id\\n        duration\\n        caption\\n        likeCount\\n        realLikeCount\\n        coverUrl\\n        coverUrls {\\n          cdn\\n          url\\n          __typename\\n        }\\n        photoUrls {\\n          cdn\\n          url\\n          __typename\\n        }\\n        photoUrl\\n        liked\\n        timestamp\\n        expTag\\n        animatedCoverUrl\\n        stereoType\\n        videoRatio\\n        profileUserTopPhoto\\n        __typename\\n      }\\n      canAddComment\\n      currentPcursor\\n      llsid\\n      status\\n      __typename\\n    }\\n    hostName\\n    pcursor\\n    __typename\\n  }\\n}\\n"}'
    # data = '{"operationName":"visionProfilePhotoList","variables":{"userId":"3x3kpid44cdd3y9","pcursor":"1.624744212863E12","page":"profile"},"query":"query visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\\n    result\\n    llsid\\n    webPageArea\\n    feeds {\\n      type\\n      author {\\n        id\\n        name\\n        following\\n        headerUrl\\n        headerUrls {\\n          cdn\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      tags {\\n        type\\n        name\\n        __typename\\n      }\\n      photo {\\n        id\\n        duration\\n        caption\\n        likeCount\\n        realLikeCount\\n        coverUrl\\n        coverUrls {\\n          cdn\\n          url\\n          __typename\\n        }\\n        photoUrls {\\n          cdn\\n          url\\n          __typename\\n        }\\n        photoUrl\\n        liked\\n        timestamp\\n        expTag\\n        animatedCoverUrl\\n        stereoType\\n        videoRatio\\n        profileUserTopPhoto\\n        __typename\\n      }\\n      canAddComment\\n      currentPcursor\\n      llsid\\n      status\\n      __typename\\n    }\\n    hostName\\n    pcursor\\n    __typename\\n  }\\n}\\n"}'
    # data = json.dumps(data)
    # follow_json = requests.post(url=url, headers=headers, data=data).json()
    # logiprint(data)
    cookiesidx = 0

    while True:
        try:

            headers = headerss[cookiesidx]
            cookies = cookiess[cookiesidx]
            # cookies['did'] = kwaiutils.gen_did()
            cookiesidx = (cookiesidx + 1) % len(cookiess)
            if debugMode:
                logger.info(headers)
                logger.info(cookies)
                logger.info(json_data)
                logger.info('正在获取 data {}'.format(json_data))
            # print(headers)
            # print(cookies)
            # print(json_data)
            shuaxin(headers, cookies)
            response = requests.post('https://www.kuaishou.com/graphql', headers=headers, cookies=cookies,
                                     json=json_data,
                                     timeout=10)
            if debugMode:
                logger.info('{}'.format(response.text))
            data_json = response.json()
            if debugMode:
                logger.info(data_json)
            break
        except Exception as e:
            traceback.print_exc()
            sleep_dis(2)
    if debugMode:
        logger.info(data_json)
    return data_json


class DownAndMoveThread(threading.Thread):
    def __init__(self, video_uptime, user_name, author, author_id, video_id, video_name, video_url, vkds):
        threading.Thread.__init__(self)
        self.user_name = user_name
        self.author = author
        self.author_id = author_id
        self.video_uptime = video_uptime
        self.video_id = video_id
        self.video_name = video_name
        self.video_url = video_url
        self.vkds = vkds

    def run(self):
        f_name = '小视频_快手视频_{}_{}_{}_{}_{}_{}.mp4'.format(self.video_uptime, self.user_name, self.author,
                                                                self.author_id,
                                                                self.video_id,
                                                                self.video_name)
        cmd1 = 'aria2c --connect-timeout=10 --max-tries=0 --file-allocation=none -x 16 -s 16 -k 1M --disable-ipv6 -o "{}" "{}"'.format(
            f_name,
            self.video_url)

        if self.video_id in self.vkds:

            logger.info('{} 已经下载'.format(f_name))
            return
        else:
            logger.info('{} 开始下载'.format(f_name))
            os.system(cmd1)
            record_ok_path_ook = os.path.join(record_ok_path, self.user_name)
            if not os.path.exists(record_ok_path_ook):
                os.makedirs(record_ok_path_ook)
            # record_ok_path = record_ok_path_ook
            if not os.path.exists(os.path.join(record_ok_path_ook, f_name)):
                shutil.move(f_name, record_ok_path_ook)
            if os.path.exists(os.path.join(record_ok_path_ook, f_name)):
                logger.info('insert_db({},{},{},{},{})'.format(self.author_id, self.author, self.video_id, f_name,
                                                               self.video_url))
                trytime = 0
                trymax = 5
                insert_db(self.author_id, self.author, self.video_id, f_name, self.video_url)
                logger.info(
                    'insert_db({},{},{},{},{}) OK'.format(self.author_id, self.author, self.video_id, f_name,
                                                          self.video_url))
                sleep_dis(2)
                # while trytime < trymax:
                #     trytime += 1
                #     try:
                #         insert_db(self.author_id, self.author, self.video_id, f_name, self.video_url)
                #         logger.info(
                #             'insert_db({},{},{},{},{}) OK'.format(self.author_id, self.author, self.video_id, f_name,
                #                                                self.video_url))
                #     except Exception as e:
                #         traceback.print_exc()
                #         sleep_dis(2)


def deal_author_mul(id, user_name):
    with ThreadPoolExecutor(max_workers=1) as executor:
        logger.info('读取数据库 {}'.format(id))
        vkds = get_downloaded_from_db(id)
        logger.info('数据库读取完毕 {}'.format(id))
        num = 0
        # 循环下载视频，直到 page == 'no_more'
        page = ''
        global ck
        global ua
        global req_data_cookies_global
        while page != 'no_more':
            sleep_dis(1)
            logger.info("page = {}".format(page))
            # time.sleep(1)
            # sleep_dis(2)
            if debugMode:
                logger.info('{} {}'.format(id, page))
            data = req_data(id, page)
            if debugMode:
                logger.info('{}'.format(data))
            # 获取翻页的参
            dflag = False
            while True:
                try:
                    next_page_Pcursor = data['data']['visionProfilePhotoList']['pcursor']
                    if next_page_Pcursor == None:
                        pass
                    else:
                        page = next_page_Pcursor
                    break
                except:
                    logger.info(data)
                    if 'result' in data:
                        if data['result'] == 2:
                            global req_cookies
                            req_cookies['did'] = random.choice(webdids)
                            logger.info('req_cookies["did"] -> {}'.format(req_cookies['did']))
                            logger.info('请求出错, 2秒后重试')
                            sleep_dis(2)
                            data = req_data(id, page)
                    else:
                        sleep_dis(2)
                        data = req_data(id, page)
                        if debugMode:
                            logger.info('{}'.format(data))
                    ua = getUa()
                    # did_global = getDid()
                    # ck = cktmp.format(did_global)
                    # req_data_cookies_global = getCookies()
                    # sleep_dis(2)
            # logger.info(next_page_Pcursor)
            data_list = data['data']['visionProfilePhotoList']['feeds']
            data_list_len = len(data_list)
            hulue_len = 0
            for item in data_list:
                num = num + 1
                # logger.info(item['photo'])
                # pprint.pprint(item)
                video_id = item['photo']['id']

                video_name = item['photo']['caption']
                video_url = item['photo']['photoUrl']
                video_timestamp = item['photo']['timestamp']
                video_uptime = timestamp2strtime(video_timestamp)
                author = item['author']['name']
                author = strfomat(author)[:15]
                author_id = item['author']['id']
                video_name = strfomat(video_name)[:20]

                user_name = (user_name)[:15]
                # author_id = item['author']['id']
                # video_name = strfomat(video_name)[:20]

                f_name = '小视频_快手视频_{}_{}_{}_{}_{}_{}.mp4'.format(video_uptime, user_name, author, author_id,
                                                                        video_id,
                                                                        video_name)
                cmd1 = 'aria2c --connect-timeout=10 --max-tries=0 --file-allocation=none -x 16 -s 16 -k 1M --disable-ipv6 -o "{}" "{}"'.format(
                    f_name,
                    video_url)

                if video_id in vkds:
                    logger.info('{} 已经下载'.format(f_name))
                    hulue_len += 1
                    # sleep_dis(1)
                    if quickmode and hulue_len == data_list_len:
                        logger.info('快速模式开启 忽略后面作品')
                        sleep_dis(2)
                        return
                    else:
                        continue
                logger.info('{} 开始下载'.format(f_name))
                dflag = True
                damt = DownAndMoveThread(video_uptime, user_name, author, author_id, video_id, video_name, video_url,
                                         vkds)
                if not debugMode:
                    executor.submit(damt.run)
                    # damt.start()
            if dflag:
                sleep_dis(2)
                dflag = False


# 处理单个主播
def deal_author(id):
    # count = count + 1
    # print(f'第{count}位关注：{id} 全部视频下载中...')
    vkds = get_downloaded_from_db(id)
    num = 0
    # 循环下载视频，直到 page == 'no_more'
    page = ''
    while page != 'no_more':
        time.sleep(1)
        data = req_data(id, page)
        logger.info(data)
        # 获取翻页的参数
        next_page_Pcursor = data['data']['visionProfilePhotoList']['pcursor']
        page = next_page_Pcursor
        # logger.info(next_page_Pcursor)
        data_list = data['data']['visionProfilePhotoList']['feeds']
        for item in data_list:
            num = num + 1
            # logger.info(item['photo'])
            # pprint.pprint(item)
            video_id = item['photo']['id']

            video_name = item['photo']['caption']
            video_url = item['photo']['photoUrl']
            video_timestamp = item['photo']['timestamp']
            video_uptime = timestamp2strtime(video_timestamp)
            author = item['author']['name']
            author = strfomat(author)[:15]

            user_name = (user_name)[:15]
            author_id = item['author']['id']
            video_name = strfomat(video_name)[:20]

            f_name = '小视频_快手视频_{}_{}_{}_{}_{}_{}.mp4'.format(video_uptime, user_name, author, author_id,
                                                                    video_id,
                                                                    video_name)
            cmd1 = 'aria2c --connect-timeout=10 --max-tries=0 --file-allocation=none -x 16 -s 16 -k 1M --disable-ipv6 -o "{}" "{}"'.format(
                f_name,
                video_url)

            if video_id in vkds:

                logger.info('{} 已经下载'.format(f_name))
                continue
            else:
                logger.info('{} 开始下载'.format(f_name))
                os.system(cmd1)
                if not os.path.exists(os.path.join(record_ok_path, f_name)):
                    shutil.move(f_name, record_ok_path)
                if os.path.exists(os.path.join(record_ok_path, f_name)):
                    logger.info('insert_db({},{},{},{},{})'.format(author_id, author, video_id, f_name, video_url))
                    try:
                        insert_db(author_id, author, video_id, f_name, video_url)
                    except Exception as e:
                        traceback.print_exc()

            # print('{} {} {}'.format(video_name, author, video_url))


def req_follow_data(url, pcursor, ck, ua, selfid):
    # 请求头
    follow_headers['Referer'] = 'https://www.kuaishou.com/profile/{}'.format(selfid)
    json_data = {
        'operationName': 'visionProfileUserList',
        'variables': {
            'ftype': 1,
            'pcursor': '{}'.format(pcursor),
        },
        'query': 'query visionProfileUserList($pcursor: String, $ftype: Int) {\n  visionProfileUserList(pcursor: $pcursor, ftype: $ftype) {\n    result\n    fols {\n      user_name\n      headurl\n      user_text\n      isFollowing\n      user_id\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n',
    }

    # response = requests.post('https://www.kuaishou.com/graphql', headers=headers, cookies=cookies, json=json_data)

    # 请求参数
    # data = {
    #     'operationName': 'visionProfileUserList',
    #     'query': 'query visionProfileUserList($pcursor: String, $ftype: Int) {\n  visionProfileUserList(pcursor: '
    #              '$pcursor, ftype: $ftype) {\n    result\n    fols {\n      user_name\n      headurl\n      '
    #              'user_text\n      isFollowing\n      user_id\n      __typename\n    }\n    hostName\n    pcursor\n   '
    #              ' __typename\n  }\n}\n',
    #     'variables': {'ftype': 1, 'pcursor': pcursor}
    # }
    # data = json.dumps(data)
    follow_json_res = requestplus(req_type='post', req_url=url, req_headers=follow_headers, req_cookies=follow_cookies,
                                  req_json=json_data)
    follow_json = follow_json_res.json()
    # follow_json = requests.post(url=url, headers=headers, data=data, cookies=cookies).json()
    # pprint.pprint(follow_json)
    return follow_json


# 获取全部关注的id
def get_all_ids(url, page, ck, ua, selfid):
    id_list = []
    num = sign = 0
    count = 0
    # 循环保存id，直到 Pcursor == 'no_more'
    add_pre_flag = True
    while page != 'no_more':
        time.sleep(1)
        # follow_data = req_follow_data(url, page, ck, ua, selfid)
        # # 获取翻页的参数
        # next_pcursor = follow_data['data']['visionProfileUserList']['pcursor']
        # if next_pcursor is None or next_pcursor == '':
        #     pass
        # else:
        #     page = next_pcursor
        # sign = sign + 1
        # logger.info(f'第{sign}页:{next_pcursor}')
        # fols_list = follow_data['data']['visionProfileUserList']['fols']
        fols_list = []
        if add_pre_flag:
            add_pre_flag = False
            folspre = [
                {'user_name': '优乐美_小美_艺轩妈咪', 'user_id': '3x3jjhycc4y9kcw'},
                                {'user_id': '3xqrbn87ifem5n6', 'user_name': '优乐美_小美_艺轩妈咪'},
                {'user_id': '3xxfie67g5jibpy', 'user_name': '优乐美_小美_艺轩妈咪'},
                {'user_id': '3x55h5pbmsxguh9', 'user_name': '优乐美_小美_艺轩妈咪'},
{'user_name': '杨瘦瘦', 'user_id': '3xrig6rjn73k9n4'},
                {'user_name': '杨瘦瘦', 'user_id': '3xcd7mqz9qfga4i'},
                {'user_name': '杨瘦瘦', 'user_id': '3xbfkmdatxvvutk'},
                {'user_name': '杨瘦瘦', 'user_id': '3xr4n5kryy7c5wi'},
                {'user_name': '杨瘦瘦', 'user_id': '3x97uhep52ifnna'},
                {'user_name': '杨瘦瘦', 'user_id': '3xzsykkexkubgq2'},
                {'user_name': '杨瘦瘦', 'user_id': '3xvcwydjk6ygfhw'},

                {'user_name': '李蕊_大淇淇', 'user_id': '3xhqb2rdbph68m9'},

                {'user_name': '张晶', 'user_id': '3xm83e4vui3auna'},


                {'user_name': '刘钰儿', 'user_id': '3xz838dit57a8ek'},




                {'user_name': '陈不凡', 'user_id': '3xhr87mxq6zvesg'},



                {'user_name': '麻利亚辣', 'user_id': '3x2u8dqndxy26b4'},
                {'user_name': '好太太', 'user_id': '3x7gsm5tziy7cg4'},
                {'user_name': '张奶奶', 'user_id': '3xe55wn4x68ck4i'},
                {'user_name': '淘淘妈', 'user_id': '3xhksk373pjufba'},
                {'user_name': '有恩', 'user_id': '3xrh83cdrgaxuqg'},
                {'user_name': '有恩', 'user_id': '3xsfz6fcq6q6nxg'},



                {'user_name': '丽御姐', 'user_id': '3xvd3scd4iiqr5w'},
                {'user_name': '杨梦艺', 'user_id': '3xw6zpexkzmnzfg'},
                {'user_name': '劳务_猫猫_鸿富', 'user_id': '3x8nyrnrepvszz2'},
                {'user_name': '小吉_小吉很酷', 'user_id': '3x4rg4c7fpcm389'},
                {'user_name': '娜娜', 'user_id': '3xjiik3dd2n5rg9'},
                {'user_name': '娜娜', 'user_id': '3xft39fxxhrwbfg'},
                {'user_name': '娜娜', 'user_id': '3xy8x82nmb54yq2'},
                {'user_name': '劳务_嘎嘎', 'user_id': '3xd4qzbk3rkr96g'},
                {'user_name': '劳务_嘎嘎', 'user_id': '3xybttjzucw8xi2'},
                {'user_name': '立米儿', 'user_id': '3xpeja8rmgyvvwk'},
                {'user_name': '立米儿', 'user_id': '3xpkiiizsa2hbgg'},
                {'user_name': '立米儿', 'user_id': '3xzay6vd8794g4s'},
                {'user_name': '李艺菲', 'user_id': '3xqvy226y497jg2'},
                {'user_name': '权v', 'user_id': '3xq82p2fyij8aqa'},
                {'user_name': '天天_小妮_Ania', 'user_id': '3xgtr8iwh3jarw2'},
                {'user_name': '紫嫣', 'user_id': '3x2h56thvf6g4q6'},
                {'user_name': '紫嫣', 'user_id': '3x9ia6a7gc5fx6i'},


                {'user_name': '汐汐子', 'user_id': '3xa9pw25ird4kmw'},
                {'user_name': '婉儿', 'user_id': '3x4ifgka2kqucpi'},
                {'user_id': '3xza5ew7yteaz6g', 'user_name': '一路邦_邦视'},
                {'user_name': '梁圣帝', 'user_id': '3xhqcg4q5wedd59'},
                {'user_name': '梁圣帝', 'user_id': '3xp9kvqhm8q3hhw'},
                {'user_name': '孟老师', 'user_id': '3x2qh22wtbzzhca'},
                {'user_name': '速溶小高', 'user_id': '3x8ry3dmiadmubi'},
                {'user_name': '程彤颜', 'user_id': '3xzk84uhviqijdw'},
                {'user_name': '李音', 'user_id': '3xu8drhcygc4bfs'},
                {'user_name': '李音', 'user_id': '3x573dt9qxefksw'},
                {'user_name': '妮妮子', 'user_id': '3xb3ifssy5sabns'},
                {'user_name': '张笑笑', 'user_id': '3xg5svwsnfpst8u'},
                {'user_name': '劳务_小夏', 'user_id': '3xhe2kzxp9y4q6u'},
                {'user_name': '小如', 'user_id': '3xgpjt2dehpshu4'},
                {'user_name': '可可', 'user_id': '3x5h429scy9eyis'},
                {'user_name': '香秀', 'user_id': '3xkryv762z8fauy'},
                {'user_name': '王可爱', 'user_id': '3xatfgs46axx3zg'},
                {'user_name': '9球', 'user_id': '3x7muas97hg6bdu'},

                {'user_id': '3x7jbzwwn3ygdsy', 'user_name': '昭昭'},
                {'user_id': '3x4xknytbmzjkjw', 'user_name': '芸儿'},
                {'user_id': '3x2cagj5xj269jm', 'user_name': '糕冷'},
                {'user_id': '3xaj876ikstq9n9', 'user_name': '佳哆宝'},
                {'user_id': '3xb5jmymnsnpkas', 'user_name': '丁一一'},
                {'user_id': '3x3keeuxnii623k', 'user_name': '小雪'},
                {'user_id': '3xkbfsip532nhke', 'user_name': 'BB酱'},
                {'user_id': '3xdzc63rsx95gam', 'user_name': '糖糖'},

                {'user_id': '3xt99f2699sf5rg', 'user_name': '玖儿'},
                {'user_id': '3xi3uaqvujyvd8q', 'user_name': '辣妈_麒麟_小鸡'},
                {'user_id': '3xgcwbph3z3ybqc', 'user_name': '辣妈_麒麟_小鸡'},
                {'user_id': '3x3vxpbyzfjsy42', 'user_name': '辣妈_麒麟_小鸡'},
                {'user_id': '3xsd4vt68kz945k', 'user_name': '美洲豹'},
                {'user_id': '3x8xf5ujgvbbtme', 'user_name': 'Karla周周'},
                {'user_id': '3xwv7mkzn53jmym', 'user_name': '兰州大姐'},
                {'user_id': '3x3nk47rr3xg3eu', 'user_name': '黑沢樱里'},
                {'user_id': '3xaewvfr5w2vgig', 'user_name': '江小帆帆'},
                {'user_id': '3xnpvx77mq9qtn4', 'user_name': '利世'},
                {'user_id': '3xfjbyue4h9hq42', 'user_name': '大飞_飞飞_小鸡_飞飞以飞飞_大飞起来了'},
                {'user_id': '3x4jt5rwyfj3dag', 'user_name': 'CardiP'},
                {'user_id': '3x5bdnzkwgsmb2e', 'user_name': '苏苏'},
                {'user_id': '3xbn638aqp8jmk4', 'user_name': '劳务_林妹妹'},
                {'user_id': '3xc8nz6a6w7qehs', 'user_name': '劳务_薇姐'},
                {'user_id': '3xy2y6mjn6wc5ya', 'user_name': '劳务_薇姐'},
                {'user_id': '3xx4t6a6gvin6ks', 'user_name': '甜甜圈'},
                {'user_id': '3x6te3eyggnqd8k', 'user_name': '九姨'},
                {'user_id': '3xmb9hkhfvqrehg', 'user_name': '九姨'},
                {'user_id': '3xj72mp797xsrvk', 'user_name': '强妈'},
                {'user_id': '3xetyvuvxei8s2y', 'user_name': '强妈'},
                {'user_id': '3xwmt6nhinw42r4', 'user_name': 'BOOM'},
                {'user_id': '3xqgwu5egdfbpee', 'user_name': '小夏_夏笙姑娘'},
                {'user_id': '3xian7hxzvvw9fk', 'user_name': '小夏_夏笙姑娘'},
                {'user_id': '3xc23wp9k6w85ay', 'user_name': '蛇妖'},
                {'user_id': '3xxmjkaitnfq5ni', 'user_name': '卡卡'},
                {'user_id': '3xgaeed4yz82x6c', 'user_name': '于小爱'},
                {'user_id': '3xgm6v323amjex2', 'user_name': '小香香'},
                {'user_id': '3xatcfe2z2trsxi', 'user_name': '司司'},
                {'user_id': '3xst9zvg2pywprk', 'user_name': '红女'},
                {'user_id': '3xkw2c2wyrk9nby', 'user_name': '红女'},
                {'user_id': '3xht2rs6ju9x49q', 'user_name': '红女'},
                {'user_id': '3xef942u7z9ktja', 'user_name': '红女'},
                {'user_id': '3xf8ztwzm9g7bbi', 'user_name': '知了'},
                {'user_id': '3xa8buczac9pj9e', 'user_name': '知了'},
                {'user_id': '3xt3c3553tm8x7a', 'user_name': '辣妈麟麟'},
                {'user_id': '3xgd9nqxmmc6qv6', 'user_name': '辰妈'},
                {'user_id': '3xgw35nvyjj9ewc', 'user_name': '辰妈'},
                {'user_id': '3xjk4fa68a5qze6', 'user_name': '辰妈'},
                {'user_id': '3xv93nsbf4dfzqe', 'user_name': '阿美雅'},
                {'user_id': '3xw5knnw93y6xvw', 'user_name': '笑个球'},
                {'user_id': '3xpk4hmixdnguf9', 'user_name': '思思'},
                {'user_id': '3x3y8nz5n2rzmpy', 'user_name': '女侠'},
                {'user_id': '3xjji6fhhyrjvfm', 'user_name': '女侠'},
                {'user_id': '3xnpm68r9253xdg', 'user_name': '恬老师'},
                {'user_id': '3xj49bpts9c2zn2', 'user_name': '糊涂小y'},
                {'user_id': '3x3aqkveu5qe6mk', 'user_name': '林桐'},
                {'user_id': '3x6xmcmsbdskfju', 'user_name': '劳务_酥酥'},
                {'user_id': '3xn6dx5x5fbtswe', 'user_name': '琳铛'},
                {'user_id': '3xzc64km7h9p87q', 'user_name': '琳铛'},
                {'user_id': '3xkqmbh7vuka7qk', 'user_name': '琳铛'},
                {'user_id': '3xi9wd9uht98ytw', 'user_name': '小团嫂_团子妈'},
                {'user_id': '3xvyiunyhrjabrc', 'user_name': '小团嫂_团子妈'},
                {'user_id': '3xtffejp9524dqe', 'user_name': '小团嫂_团子妈'},
                {'user_id': '3x8wsqwperzzpiq', 'user_name': '小团嫂_团子妈'},
                {'user_id': '3xnfyqky4bp6dzi', 'user_name': '柳梦寒'},
                {'user_id': '3xj8qb88f4mkfkg', 'user_name': '柳梦寒'},
                {'user_id': '3xwjt3hkptmsxfe', 'user_name': '柳梦寒'},
                {'user_id': '3xzmrn7y4ed8jhc', 'user_name': '柳梦寒'},
                {'user_id': '3xbv4uejih4vfd4', 'user_name': '柳梦寒'},
                {'user_id': '3x278xsukgfuvmq', 'user_name': '柳梦寒'},
                {'user_id': '3xzkx24t444wcia', 'user_name': '劳务_小妈职优乐'},
                {'user_id': '3xdxu243cxizbvw', 'user_name': '劳务_小妈职优乐'},

                {'user_id': '3x3ebuzau6hb7vs', 'user_name': '晴大美'},
                {'user_id': '3x4e4bpnn53fsu4', 'user_name': '晴大美'},
                {'user_id': '3x977hkdgf3fsqq', 'user_name': '岚岚'},
                {'user_id': '3xb8msfve2hvhsq', 'user_name': 'Mimi蛋儿'},
                {'user_id': '3xrbp89qjmwkhfm', 'user_name': 'Mimi蛋儿'},
                {'user_id': '3xjhj4qq4bq3rji', 'user_name': '小易_晓碧碧_小易bibi'},
                {'user_id': '3xkgz72z3ya8yfi', 'user_name': '小易_晓碧碧_小易bibi'},
                {'user_id': '3xyupm29vxtcy59', 'user_name': '小易_晓碧碧_小易bibi'},
                {'user_id': '3xgjed96bcuipim', 'user_name': '小易_晓碧碧_小易bibi'},
                {'user_id': '3xmkmtiphuqhd66', 'user_name': '小易_晓碧碧_小易bibi'},
                {'user_id': '3xtwzp7b2eep5eu', 'user_name': '阿月'},
                {'user_id': '3x4954mqewb6cka', 'user_name': '奥特雯'},
                {'user_id': '3xxiy9m7awpc85m', 'user_name': '王辛迪'},
                {'user_id': '3xkqx6sw4zatd2i', 'user_name': '绮里嘉'},
                {'user_id': '3x8w8g2niyvkegw', 'user_name': '周妍希'},
                {'user_id': '3x7wmvtgmc5jty9', 'user_name': '周妍希'},
                {'user_id': '3x8rgc35map5chm', 'user_name': '董萌萌'},
                {'user_id': '3xyvhhmtg4sckv9', 'user_name': '爱丽丝'},
                {'user_id': '3xd8ry2vf3njd8c', 'user_name': '爱丽丝'},
                {'user_id': '3xg6qsieztntruc', 'user_name': '樱花一朵'},
                {'user_id': '3xkp3rtm2i5i9h2', 'user_name': '王俪丁'},
                {'user_id': '3xr2zfrdmdviqyi', 'user_name': '尚美街拍'},
                {'user_id': '3xg7g6cfhpyjxhy', 'user_name': '美羊羊'},
                {'user_id': '3xbkgstus9gn5qi', 'user_name': '欣欣'},
                {'user_id': '3xxze8cmftukgua', 'user_name': 'miki'},
                {'user_id': '3xbs4zrpteurpki', 'user_name': '七喜'},
                {'user_id': '3xr4min6v6zj4fm', 'user_name': '有夕大人'},
                {'user_id': '3x9yuhrt3u8swy2', 'user_name': '劳务_伊姐'},
                {'user_id': '3xphd4ka6duc6gy', 'user_name': '晨洁'},
                {'user_id': '3x89ntazp5ejrag', 'user_name': '胖嘟嘟'},
                {'user_id': '3x9dvqn4sqs65rw', 'user_name': '丽丽酱'},
                {'user_id': '3xbjcinjezd7pbg', 'user_name': '劳务_王贝贝'},
                {'user_id': '3xmuwnvwya9a6ds', 'user_name': '程儿'},
                {'user_id': '3xincx4r7bmpgeg', 'user_name': '老夫妻'},
                {'user_id': '3xw6i2rhxyg7fb2', 'user_name': '郭大小姐'},
                {'user_id': '3xi2i6w6umx2fmg', 'user_name': '小苏嫣'},
                {'user_id': '3xhif7ahzjh9t5s', 'user_name': '辣妈_麒麟'},
                {'user_id': '3xfnjsfwbkg9nqw', 'user_name': '默宝儿'},
                {'user_id': '3xnqrvit7w5v6rs', 'user_name': '默宝儿'},
                {'user_id': '3xkfbhxfttn25a9', 'user_name': '王莹莹_小莹子_汤圆妈'},
                {'user_id': '3xe84268qfbgsfs', 'user_name': '王莹莹_小莹子_汤圆妈'},
                {'user_id': '3xuv5wcxxykfqmg', 'user_name': '库库'},
                {'user_id': '3x36qjpwzxxit9q', 'user_name': '佟小琪_奶狼'},
                {'user_id': '3xwi9tadznq7vqs', 'user_name': '佟小琪'},
                {'user_id': '3x7xessm4jb26xy', 'user_name': '佟小琪'},
                {'user_id': '3xhtbv3d5mmnmuc', 'user_name': '开心你果果'},
                {'user_id': '3ximuttamwbyqt2', 'user_name': '素素'},
                {'user_id': '3xuwqs2u2hk5tzq', 'user_name': 'SirenLANBO'},
                {'user_id': '3x6tiqajeti2rms', 'user_name': '可爱洋'},
                {'user_id': '3xejjkk28giarx9', 'user_name': '芊语芊寻'},
                {'user_id': '3xej4nnt39t8kq4', 'user_name': '大恬'},
                {'user_id': '3xca5zvbg9z2fha', 'user_name': '大恬'},
                {'user_id': '3xnjr6dh8zcrffe', 'user_name': '李李'},
                {'user_id': '3xhi6is54qmvd8a', 'user_name': '静宝贝'},
                {'user_id': '3x9uz687sr67dxi', 'user_name': '冷诗寒'},
                {'user_id': '3xmib86twakzauu', 'user_name': '李思淇'},
                {'user_id': '3xeedprn8mj3hqs', 'user_name': '小六妹'},
                {'user_id': '3xamrsmidn3w6km', 'user_name': '贝拉'},
                {'user_id': '3xjgjei6kmp9q8e', 'user_name': '皮皮'},
                {'user_id': '3xdtncf99hb7zk4', 'user_name': '王雨萱'},
                {'user_id': '3xjr86qh48kvd6i', 'user_name': '兔宝妮'},
                {'user_id': '3xs4uusfbk5wy6s', 'user_name': '苗苗'},
                {'user_id': '3x4hazxygyuy859', 'user_name': '九妹_劳务'},
                {'user_id': '3x5h4ew3g6bihyq', 'user_name': '劳务_哈哈妹'},
                {'user_id': '3x5r4m2nq7irepc', 'user_name': '劳务_小鹿'},
                {'user_id': '3xqba6zp3ejdpca', 'user_name': '小龙鼠'},
                {'user_id': '3x8mpktamdibyga', 'user_name': '九妹'},
                {'user_id': '3xjwdf2vwhbxinc', 'user_name': '九姑娘'},
                {'user_id': '3xkfchn77k83mk2', 'user_name': '浅浅'},
                {'user_id': '3xb6azw3vrs4974', 'user_name': '杨月蕊'},
                {'user_id': '3xtgcv7euxvdya6', 'user_name': '张卡卡'},
                {'user_id': '3x4cuftznqju53a', 'user_name': '小六妹'},
                {'user_id': '3xns7z4y9kfb2hg', 'user_name': '罗球球'},
                {'user_id': '3xmcvjdbrsmvyh4', 'user_name': '冉潇潇'},
                {'user_id': '3xfuj8i9zmduaik', 'user_name': '小狸猫'},
                {'user_id': '3xiggmdk4venym4', 'user_name': '小狸猫'},
                {'user_id': '3xp4m6i4s4p2zcq', 'user_name': '燕宝'},
                {'user_id': '3xysk9xah9a8pdc', 'user_name': '艳子'},
                {'user_id': '3x3rye75rqqmqpc', 'user_name': 'SUKI_酱酱'},
                {'user_id': '3x89cp5kss8rzsq', 'user_name': '李思淇'},
                {'user_id': '3xmbnkhsjccgptc', 'user_name': '李思淇'},
                {'user_id': '3x6bg7rrwstsmmu', 'user_name': '姜秘书'},
                {'user_id': '3xusjfkxxkanave', 'user_name': '霜霜喝大力'},
                {'user_id': '3xvv7yh77b66spc', 'user_name': '高温柔'},
                {'user_id': '3xwtrcv4s7hefe4', 'user_name': '冷一'},
                {'user_id': '3x5wsfcrzmknc2m', 'user_name': '雪花莹莹'},
                {'user_id': '3xtx3i9j7e35vg9', 'user_name': '王大美少妇'},
                {'user_id': '3xsut87frp84bdk', 'user_name': '蜜丝燕'},
                {'user_id': '3x85qtps94ykxqy', 'user_name': '胡萝卜'},
                {'user_id': '3x5d5snh33dbhzw', 'user_name': '1221500'},
                {'user_id': '3x7jw73cd83pcam', 'user_name': '多肉小野猫'},
                {'user_id': '3x7setmy7vcfm4g', 'user_name': '奶雯'},
                {'user_id': '3xspdj33yhpdcy6', 'user_name': '黑冰科技'},
                {'user_id': '3xykf2qhq5kkezk', 'user_name': '巧小君'},
                {'user_id': '3xk3j8k7hj4n992', 'user_name': '婷婷与直男'},
                {'user_id': '3xwsv38zhu6nhsq', 'user_name': '小杵忆'},
                {'user_id': '3xxcvm2bttwekxq', 'user_name': '海艳'},
                {'user_id': '3x8v4n2ddh9jiey', 'user_name': '一口越'},
                {'user_id': '3xha4nwgmjz8jtm', 'user_name': '花花_一口越'},
                {'user_id': '3x37xde3w4vtjqe', 'user_name': '花嫂'},
                {'user_id': '3x4suvbzenxj9zw', 'user_name': '申辣辣'},
                {'user_id': '3xkkm5daf9yedza', 'user_name': '牛奶秋刀姨'},
                {'user_id': '3xwx34hpj7ttisy', 'user_name': '卡通百科_老王'},
                {'user_id': '3xhi8is4t8vq7xq', 'user_name': '吴春怡'},
                {'user_id': '3xi75gusgf6iz9g', 'user_name': '吴春怡'},
                {'user_id': '3x47yjpb6tux4f4', 'user_name': '小美_Y小美'},
                {'user_id': '3xffjdejtty5haa', 'user_name': '小葵姐姐'},
                {'user_id': '3xwnt59zqri6bza', 'user_name': '黄星星'},
                {'user_id': '3x6z8j5g3kzvmwq', 'user_name': '炒粉'},
                {'user_id': '3x2kmn3kgfpydvg', 'user_name': '甜甜'},
                {'user_id': '3xc3ifk6ccwhyb9', 'user_name': '桃沢樱'},
                {'user_id': '3xya5mxnr9b4wm9', 'user_name': '依一'},
                {'user_id': '3x7mra3wg7j4wr4', 'user_name': '锦缎儿'},
                {'user_id': '3xqe2sbtcyjk9v4', 'user_name': '程儿'},
                {'user_id': '3xmq6gzwu23tuc2', 'user_name': '劳务_翠翠'},
                {'user_id': '3xvsp4iq93mt3sm', 'user_name': 'Mikki'},
                {'user_id': '3x3u4tni42afnps', 'user_name': '小多_小明哥哥'},
                {'user_id': '3x36xeem5pag8im', 'user_name': '小多_小明哥哥'},
                {'user_id': '3xmgik685em2pzu', 'user_name': '小当家_小明哥哥'},
                {'user_id': '3x7gra4bv5ze2nw', 'user_name': '小甜_小明哥哥'},
                {'user_id': '3xucyzypyt5nve4', 'user_name': '小琪_小明哥哥'},
                {'user_id': '3xy7b49ww72re99', 'user_name': '小丸子_小明哥哥'},
                {'user_id': '3xi5g4ncxfjjs5e', 'user_name': '小薇'},
                {'user_id': '3xpns3dws2rgmhc', 'user_name': '小甜_小明哥哥'},
                {'user_id': '3x543wfj2hk4by2', 'user_name': '小宝_小明哥哥'},
                {'user_id': '3x5562aj8ccqnme', 'user_name': '阿硕小丸子'},
                {'user_id': '3xsd8dxe9yv7hcq', 'user_name': '阿硕小丸子'},
                {'user_id': '3xp4b3cnag7xf8q', 'user_name': '美妮'},
                {'user_id': '3x7ey79xss27mey', 'user_name': '微胖小欣儿'},
                {'user_id': '3xcdv6s6r356upu', 'user_name': '传祺版纳'},
                {'user_id': '3xqjgmb6r22cmzi', 'user_name': '大美'},
                {'user_id': '3xywpj7rvfwkd84', 'user_name': '欣妹儿'},
                {'user_id': '3xywg4ez4wtgcew', 'user_name': '七七'},
                {'user_id': '3x735epf3sq47pq', 'user_name': '劳务_猪猪'},
                {'user_id': '3xy4xc3nyg55dz2', 'user_name': '余余儿'},
                {'user_id': '3xearprcbs3futu', 'user_name': '婷婷'},
                {'user_id': '3xphetkm6q3bguk', 'user_name': '雨桐'},
                {'user_id': '3xs2xxjhwy4ny6i', 'user_name': '漂亮的大姨姐'},
                {'user_id': '3x2tfkicjnyr8ke', 'user_name': '漂亮的大姨姐'},
                {'user_id': '3xy2g2ky4u4hnqw', 'user_name': '比亚迪柳州_比亚迪海洋柳州迪润4S店'},
                {'user_id': '3xmyw4gih9fsw9u', 'user_name': '神仙姐姐'},
                {'user_id': '3x9gkn6de2jg3n4', 'user_name': '金希儿'},
                {'user_id': '3x4g9ehvj4w8rza', 'user_name': '西西姐'},
                {'user_id': '3xsn2h6cz92w3bk', 'user_name': '巧克妮'},
                {'user_id': '3xi4cg7cae8k9ge', 'user_name': '金好好'},
                {'user_id': '3xqt97f7ym4kmew', 'user_name': '郑瑞妤'},
                {'user_id': '3xmgi6zgmhxzqs6', 'user_name': 'Luna挽月'},
                {'user_id': '3xv3mhhq67gefxm', 'user_name': '兔子老师'},
                {'user_id': '3xm8g3qmb8as7ey', 'user_name': '柔柔兔子'},
                {'user_id': '3xfuckvwkf4csq6', 'user_name': '芒果三文鱼'},
                {'user_id': '3xe5nw6nvm5ihns', 'user_name': '玲姨'},
                {'user_id': '3x4atcjxc5zi6uw', 'user_name': '梓琳_琳琳小公主'},
                {'user_id': '3xbp75frwvtqa4a', 'user_name': '你的萌_萌萌_小刘'},
                {'user_id': '3xiwje65xmjcng2', 'user_name': '马自达合肥'},
                {'user_id': '3x6eftbksgnw4gq', 'user_name': '柔琴'},
                {'user_id': '3x8xngp8k8tmzbs', 'user_name': '柔琴'},
                {'user_id': '3xb2gzjnk3qmgei', 'user_name': '思柠'},
                {'user_id': '3x6we685mjzw7c4', 'user_name': '雪儿'},
                {'user_id': '3xvij3ci86gexae', 'user_name': '琴琴'},
                {'user_id': '3x5tzhxqage5rnw', 'user_name': '琴琴'},
                {'user_id': '3xc8h9whe7qjt3m', 'user_name': '小蕊寻翠'},
                {'user_id': '3xstn2ergexesvy', 'user_name': '丝爷'},
                {'user_id': '3xgdwbe7jbvrfe2', 'user_name': '丝爷'},
                {'user_id': '3x3hufmx26vdmeu', 'user_name': 'Kwe临也'},
                {'user_id': '3xtgknan6tek6a4', 'user_name': 'Kwe临也'},
                {'user_id': '3x59sv95iy6mrf9', 'user_name': '小龙鼠'},
                {'user_id': '3xyzwzdxvr2smye', 'user_name': '肖肖乐'},
                {'user_id': '3xhxtkkxhnyupwi', 'user_name': '平面模特小小'},
                {'user_id': '3x4repmjauabxye', 'user_name': '小心奶茶'},
                {'user_id': '3x2n7vkhbjcj86w', 'user_name': '嫂子'},
                {'user_id': '3xmub7jddhdryja', 'user_name': '周木子'},
                {'user_id': '3xxyueb5w4eq6kw', 'user_name': '周木子'},
                {'user_id': '3xtnifjkf8dbf3g', 'user_name': '双双'},
                {'user_id': '3xqqc35ha2ycjze', 'user_name': '任小护520'},
                {'user_id': '3xhfwbhgt34kcqy', 'user_name': '甜缘'},
                {'user_id': '3xabaxv4emc8awc', 'user_name': '比亚迪新乡新迪店'},
                {'user_id': '3xcpai252weybeg', 'user_name': '有点瘦'},
                {'user_id': '3xfiqf37x49zzkk', 'user_name': '鑫萍气和'},
                {'user_id': '3xghih9aaap6zv9', 'user_name': '涗涗'},
                {'user_id': '3xzh5ajjtp4wy32', 'user_name': 'YAHAN亚含'},
                {'user_id': '3xqs7pt94vpzzv4', 'user_name': '九月'},
                {'user_id': '3xhmcusb68pxwz4', 'user_name': '梦艺_big梦艺_嫩脚'},
                {'user_id': '3xipp3fgmwkwcte', 'user_name': '安禹晴'},
                {'user_id': '3xpig5wz8fr79aq', 'user_name': '包老二_离异_嫩脚'},
                {'user_id': '3x8vm7b7mcx3q9y', 'user_name': '包老二_离异_嫩脚'},
                {'user_id': '3x44weedwfjpnyq', 'user_name': '佳宝宝'},
                {'user_id': '3xiptkpp7tz4m54', 'user_name': '程宝'},
                {'user_id': '3x32gztmyucnvrk', 'user_name': '程宝'},
                {'user_id': '3xzef3z335xqhj4', 'user_name': '容六六'},
                {'user_id': '3x2brb7gqzv4fbu', 'user_name': '喵大仙儿'},
                {'user_id': '3x5nyrzmg227bry', 'user_name': '奶茶多多'},
                {'user_id': '3xzwtekghf7gspc', 'user_name': '猴弟这是一个谜'},
                {'user_id': '3x3f9eb5dxnhb7s', 'user_name': '彤彤寶贝'},
                {'user_id': '3xukhh9868rynia', 'user_name': '金允娜_允娜姐姐'},
                {'user_id': '3xiqi3r7qn2edrq', 'user_name': '李娜'},
                {'user_id': '3x45hunqfydiam2', 'user_name': '小李老师_你的小李老师'},
                {'user_id': '3xgza3tbxmqb2fy', 'user_name': '饭饭'},
                {'user_id': '3xastyv2ztn5jw6', 'user_name': '仙姒醒啦'},
                {'user_id': '3xcd9cma722hjhc', 'user_name': '糖小糖_撩车糖小糖'},
                {'user_id': '3x27kciyxahqzxu', 'user_name': '小雪_公主小雪'},
                {'user_id': '3xzn77xq8um48ra', 'user_name': '二仙桥桥花'},
                {'user_id': '3x38rgtkfunkzra', 'user_name': '玉兔兔'},
                {'user_id': '3x7a9i8by6pa3ug', 'user_name': '小桃子'},
                {'user_id': '3xq29yepq6kyqe4', 'user_name': '桃子_小桃子_小桃子吖_巨乳'},
                {'user_id': '3xuujxvux9h56dq', 'user_name': '春姐_杨洁_杨洁耐斯_巨乳_小鸡'},
                {'user_id': '3xjngegbirf22qw', 'user_name': '阿畅_巨乳'},
                {'user_id': '3x7mvmnhkmvkg5y', 'user_name': '阿畅_巨乳'},
                {'user_id': '3x3iabhcnyqpjry', 'user_name': '小蓝蓝plus_小蓝蓝_居然小蓝蓝'},
                {'user_id': '3xdri9it2gwpktc', 'user_name': '诺一萌'},
                {'user_id': '3xrjhqxfb8gnkuq', 'user_name': '双胞胎_舒琪美琪'},
                {'user_id': '3xgiivg2q54qh3q', 'user_name': '西西'},
                {'user_id': '3xyheujfrveix8a', 'user_name': '御姐'},
                {'user_id': '3x43wrnqg48w3y4',
                 'user_name': '四喜nana_1994_四喜娜娜_四喜_nana_四喜戴娜_嫩脚'},
                {'user_id': '3xafer5imeabvdi', 'user_name': '真珠臻选_真珠_真猪_猪珠_可爱猪珠宝_嫩脚'},
                {'user_id': '3xbc2c2w56q522i', 'user_name': '熙语_巨乳_离异'},
                {'user_id': '3x5mcxa5hc8wx7e', 'user_name': '蜜桃_小姨_陈曦_曦曦'},
                {'user_id': '3x5rtseqnmxetms', 'user_name': '浮云'},
                {'user_id': '3x966vdmgnmsuxk', 'user_name': '慧子_你的秘书_蒙面女王_知心姐姐'},
                {'user_id': '3x87hswd8eccmhi', 'user_name': '慧子_你的秘书_蒙面女王_知心姐姐'},
                {'user_id': '3xaiqrqde4mmnwg', 'user_name': '慧子_你的秘书_蒙面女王_知心姐姐'},
                {'user_id': '3xd68pjaty5rycs', 'user_name': '月宝宝'},
                {'user_id': '3xfcejbhyzs825q', 'user_name': '七宝'},
                {'user_id': '3xac39uia8hxqyq', 'user_name': '七微'},
                {'user_id': '3xhriur97e3xkxs', 'user_name': '摇摆彤'},
                {'user_id': '3xr9teann83qeh9', 'user_name': '摇摆彤'},
                {'user_id': '3xjizu9ad832nyi', 'user_name': '刘舒睿'},
                {'user_id': '3x2fhzrzvt8zywc', 'user_name': '诗诗'},
                {'user_id': '3xs4cvyst4vdvae', 'user_name': 'nana_娜娜'},
                {'user_id': '3xtepmqmmfberpg', 'user_name': '姜喵喵'},
                {'user_id': '3xp7s2sj5yqbvhu', 'user_name': '王大锤子'},
                {'user_id': '3xjduyuunkvax4q', 'user_name': '小可乐'},
                {'user_id': '3x8mwkftj3mpwbu', 'user_name': '野马姐姐'},
                {'user_id': '3x9js4pna8k2xha', 'user_name': '君陌睿'},
                {'user_id': '3xwtsqk48kcvaa6', 'user_name': 'TA'},
                {'user_id': '3xpdr58i7mmt2cy', 'user_name': '陆小芊'},
                {'user_id': '3xwru98xvtgja5s', 'user_name': '嫩脚_晓晓_晓晓最可爱'},
                {'user_id': '3xsupw2mfkacwg4', 'user_name': '何雪子'},
                {'user_id': '3x4n99tsyfs5cm6', 'user_name': '茵婷_婷婷BABY'},
                {'user_id': '3xrrfnq787rej7s', 'user_name': '瑶烫门'},
                {'user_id': '3xx4js6uudkpx8u', 'user_name': '琳静'},
                {'user_id': '3xf2ckgzjbwfsug', 'user_name': '9宝宝'},
                {'user_id': '3xpmpuqq7hgdgjs', 'user_name': 'han47484'},
                {'user_id': '3xcki4crmtz5smm', 'user_name': '尤物辣辣'},
                {'user_id': '3xvp4rmjf82atb4', 'user_name': '柚子er'},
                {'user_id': '3xg2kebvbc5qfa6', 'user_name': '赵可欣'},
                {'user_id': '3xqsqx5gp6q9q46', 'user_name': '柠檬'},
                {'user_id': '3x4q7hbvydafx7m', 'user_name': '邱丽超_蒙娜丽妮'},
                {'user_id': '3xzbnb3bgvkg9sa', 'user_name': '旗袍文儿_明日香_滚烫'},
                {'user_id': '3xbug6g8eequhfu', 'user_name': '旗袍文儿_明日香_滚烫'},
                {'user_id': '3xxxw9pe8isjg3w', 'user_name': '嫩脚_你小姨_二姐'},
                {'user_id': '3x39mb5i8wjyvpy', 'user_name': '嫩脚_你小姨_二姐'},
                {'user_id': '3xv7xske77nbzhw', 'user_name': '月月'},
                {'user_id': '3xdnrqpcf9ruvzi', 'user_name': '牡丹丹'},
                {'user_id': '3xnay9n3d8kuiww', 'user_name': '牡丹丹'},
                {'user_id': '3xsud2nyd4y5biw', 'user_name': '火凤凰_青儿_嫩脚_骚妇'},
                {'user_id': '3xggwnixekhz68a', 'user_name': '火凤凰_青儿_嫩脚_骚妇'},
                {'user_id': '3xzarknb8sgwp6g', 'user_name': '张玲玲_翘臀_巨乳'},
                {'user_id': '3x3nu9mm4vp38xy', 'user_name': '悦悦_翘臀_巨乳'},
                {'user_id': '3xb7h7xggxhvji9', 'user_name': '悦悦_翘臀_巨乳'},
                {'user_id': '3xhkbvinwrb8mh4', 'user_name': '智妍'},
                {'user_id': '3xg7m8s4vvnaayc', 'user_name': '张素'},
                {'user_id': '3xwrkw5u29knxzy', 'user_name': '小草莓'},
                {'user_id': '3xdbdwz6fckrrda', 'user_name': '小草莓'},
                {'user_id': '3xe29h2vvvp4xaa', 'user_name': '克老师'},
                {'user_id': '3xwgk8tceuzsxay', 'user_name': '姜鑫_小妈_被人乱插'},
                {'user_id': '3xaxgxbjmtdpc84', 'user_name': '阿申_嫩脚_申某某唯一_幸运女神阿申'},
                {'user_id': '3xvn28nwp9azhy9', 'user_name': '阿申_嫩脚_申某某唯一_幸运女神阿申'},
                {'user_id': '3x34dcrtsnhy6q6', 'user_name': '玲儿赞'},
                {'user_id': '3xtpxj7wzkxcfrc', 'user_name': '晓庆_晓庆妹妹_巨乳_翘臀_嫩脚_骚妇'},
                {'user_id': '3x5483gs37s6wj2', 'user_name': '崔朵朵_吉林艺术学院_160_82斤'},
                {'user_id': '3xmndpixmkryu26', 'user_name': '小王_小王同学_是120斤的小王同学_大奶_巨乳_小鸡_张老师'},
                {'user_id': '3xvws79aps25ans', 'user_name': '大美丽_大美丽NEVER_成都_模特_小鸡'},
                {'user_id': '3xhszxucp93dkgs', 'user_name': '张爱玲_嫩脚'},
                {'user_id': '3xuureygp6cns3w', 'user_name': '程程_嫩脚'},
                {'user_id': '3xn7fbn85abz48q', 'user_name': '程程_嫩脚'},
                {'user_id': '3xvvd7kjr8duxqs', 'user_name': '梦琪_大奶_巨乳'},
                {'user_id': '3x654h6cxdmnxd6', 'user_name': '杨梦琪_大奶_巨乳'},
                {'user_id': '3xx2g4gukunieku', 'user_name': '杨梦琪_大奶_巨乳'},
                {'user_id': '3x8536dqn544m7y', 'user_name': '杨梦琪_大奶_巨乳'},
                {'user_id': '3xr4ifnuytth864', 'user_name': '王梦琪'},
                {'user_id': '3xuji63dfdtjpk6', 'user_name': '希妹儿_91_小鸡'},
                {'user_id': '3xqjijqvaw4pmsq', 'user_name': '大反派_小小虫'},
                {'user_id': '3xccj4f7cf56q96', 'user_name': '娜娜酱'},
                {'user_id': '3xjsmjbk63yqgpk', 'user_name': '娜娜酱'},
                {'user_id': '3xqm7zz3aydvfms', 'user_name': '娜娜酱'},
                {'user_id': '3xjjcbj5ywckhgu', 'user_name': '小仙女爱钓鱼'},
                {'user_id': '3xtfkntwimkpkvu', 'user_name': '邻家玉儿_盛业商务车'},
                {'user_id': '3xjeeab48zw8qrg', 'user_name': '邻家玉儿'},
                {'user_id': '3xhavqhpgk8rqt6', 'user_name': '邻家玉儿_盛业房车改装付文高'},
                {'user_id': '3xu7xq5uemgewkw', 'user_name': '清风皓月'},
                {'user_id': '3xmmrwsct44kf42', 'user_name': '大奶御姐'},
                {'user_id': '3xsgagwmh8wapii', 'user_name': '大奶御姐'},
                {'user_id': '3x8gtg3vqm2w2g2', 'user_name': '大奶御姐'},
                {'user_id': '3xhc3t6d5gyu494', 'user_name': '大奶御姐'},
                {'user_id': '3xmnbj3wecb7mci', 'user_name': '大奶御姐'},
                {'user_id': '3xwauypg46bnym2', 'user_name': '大奶御姐'},
                {'user_id': '3x5uvgvbjyrk5ny', 'user_name': '江西芊芊_芝士姐姐_大奶_巨乳_骚妇'},
                {'user_id': '3xqhuzqh4hhzbkg', 'user_name': '苏蒽_大奶_巨乳'},
                {'user_id': '3xqnp3cm5kg9pvk', 'user_name': '思妹儿'},
                {'user_id': '3xpah78r72z5skm', 'user_name': '思妹儿'},
                {'user_id': '3x59syzubsf569g', 'user_name': '珍之儿姐姐'},
                {'user_id': '3xfj7q7nbfw986y', 'user_name': '珍之儿姐姐'},
                {'user_id': '3xnhrtv3iwgykiq', 'user_name': '珍之儿姐姐'},
                {'user_id': '3x6i5gpjt6am3qk', 'user_name': '西西果'},
                {'user_id': '3x333ritqmzjvd6', 'user_name': '臭美小静宝'},
                {'user_id': '3xtydca265xhg6e', 'user_name': '小梅仙女'},
                {'user_id': '3xk5nc69hp6bqgs', 'user_name': '小梅仙女'},
                {'user_id': '3xngq65qub3m59s', 'user_name': '茜茜'},
                {'user_id': '3x7fjwbmsxsv7nc', 'user_name': '雅菲_北北'},
                {'user_id': '3xrmnzmv53yxcbq', 'user_name': '王思佳'},
                {'user_id': '3xwy36cs773jx24', 'user_name': '百变咔咔小苹果_小苹果'},
                {'user_id': '3x8ntyd9qd695ba', 'user_name': '百变咔咔小苹果'},
                {'user_id': '3xeec4ui9h3z4b9', 'user_name': '小跳兔'},
                {'user_id': '3xywfi9g8s4fkyk', 'user_name': '啊紫_阿紫_愫愫情闺蜜_湖南嫩脚'},
                {'user_id': '3xpfn7t7brv2k52', 'user_name': '大长腿阿紫_啊紫_阿紫_愫愫情闺蜜_湖南嫩脚'},
                {'user_id': '3xydpy3365wn3tc', 'user_name': '一只周_骚妇_嫩脚'},
                {'user_id': '3x6y9d2733cb6vw', 'user_name': '钱多多_大奶_车模_嫩脚'},
                {'user_id': '3xu3afhxn7pc6q6', 'user_name': '钱多多_大奶_车模_嫩脚'},
                {'user_id': '3xw4mexxe9ufcvg', 'user_name': '新哥_黑家发财_老公'},
                {'user_id': '3x4ubmvwkr5uz8y', 'user_name': '黑家发财_骚妇_嫩脚'},
                {'user_id': '3xnvrn9zae6v2cg', 'user_name': '街拍_简一街拍'},
                {'user_id': '3xe2w7858y5kep2', 'user_name': '双胞胎硕果妈妈'},
                {'user_id': '3xqfeduzbdrdzgm', 'user_name': '王欣妍_酱酱_兔酱11_兔酱'},
                {'user_id': '3xjzhg5uddyyzew', 'user_name': '落雨_婷婷'},
                {'user_id': '3xnd37wmjsye45u', 'user_name': '77'},
                {'user_id': '3xbyv6p99wpwbma', 'user_name': '芙蓉姐姐_大哥插过'},
                {'user_id': '3xqrvbe6wt7g3qy', 'user_name': '心如小妮儿'},
                {'user_id': '3xkjwxn6jpjecpm', 'user_name': '丹妹_王景黎_江西骚妇'},
                {'user_id': '3xnhbbk4gb6vd42', 'user_name': '蕊哥'},
                {'user_id': '3x7f9rpfisja9kq', 'user_name': '小火猪'},
                {'user_id': '3xpn45az966tc4u', 'user_name': '兔小姨'},
                {'user_id': '3xc976fng6ga2my', 'user_name': '水儿'},
                {'user_id': '3xc7t2f9z3rste4', 'user_name': '多多'},
                {'user_id': '3xr9zs8mg7vhgnc', 'user_name': '多多'},
                {'user_id': '3x3ynwmyxjye7by', 'user_name': '钱多多'},
                {'user_id': '3xag5sm4ww8zmq4', 'user_name': '于欣柔'},
                {'user_id': '3xap28dkuwuqema', 'user_name': '辣条'},
                {'user_id': '3xn5kh57zu743gu', 'user_name': '辣条'},
                {'user_id': '3xv5qaei8ghnqg6', 'user_name': '肖潇'},
                {'user_id': '3xfvkybx7c8mecm', 'user_name': '肖潇'},
                {'user_id': '3x49q995gyn8yek', 'user_name': '肖潇'},
                {'user_id': '3xwgssc2rrz8e9q', 'user_name': '肖潇'},
                {'user_id': '3xvtnj9stn39gtm', 'user_name': '肖潇'},
                {'user_id': '3xxx48b7d4h4ug4', 'user_name': '肖潇'},
                {'user_id': '3x7rngtvspdgdgw', 'user_name': '元气学姐'},
                {'user_id': '3x2xeez4kd3bx82', 'user_name': '元气学姐'},
                {'user_id': '3xrmb45y2q2gngc', 'user_name': '薇宝'},
                {'user_id': '3xrk9arqbgst9rw', 'user_name': '曹晓萍'},
                {'user_id': '3xa8dwq9dejixm9', 'user_name': '慧宝'},
                {'user_id': '3xu8yz5fe2pbii2', 'user_name': '慧宝'},
                {'user_id': '3xszrk7ksy7pzns', 'user_name': '瑶瑶'},
                {'user_id': '3x894gu4ta8n64a', 'user_name': '苏子七'},
                {'user_id': '3xiie432pna5p3g', 'user_name': '陈贝贝'},
                {'user_id': '3x6s29kztb7s48w', 'user_name': '诗诗'},
                {'user_id': '3xbazs96rgcr57q', 'user_name': '韩婧格'},
                {'user_id': '3x64rhaynrsp7f2', 'user_name': '三亚游艇小鱼'},
                {'user_id': '3xgnkaajw28ydvc', 'user_name': '厦门游艇鸭鸭'},
                {'user_id': '3x9xwa3uib3zbwi', 'user_name': '依萌_游艇春插过'},
                {'user_id': '3xbqeviqyhugcsw', 'user_name': '小李老师'},
                {'user_id': '3x87h2ai2uj4f8a', 'user_name': '刘儿'},
                {'user_id': '3xcawnek8u889qy', 'user_name': '婧燕'},
                {'user_id': '3xeg33tg46dr7q4', 'user_name': '宇霸霸'},
                {'user_id': '3xd3eb88uzcf689', 'user_name': '宇霸霸'},
                {'user_id': '3x9dr4h26y7sg3c', 'user_name': '宇霸霸'},
                {'user_id': '3xgbnh7hkxj3yxe', 'user_name': '朵妃'},
                {'user_id': '3xme3vfe2km4amk', 'user_name': '希希'},
                {'user_id': '3x78u9pq72vnzsu', 'user_name': '希希'},
                {'user_id': '3xngwjr44uudync', 'user_name': '莹莹'},
                {'user_id': '3xaa4t4tf84yd94', 'user_name': '丝袜御姐'},
                {'user_id': '3xe4nbava7vc9ki', 'user_name': '丝袜御姐'},
                {'user_id': '3xs3y55k6atxq8k', 'user_name': '丝袜御姐'},
                {'user_id': '3xns4bnqqzg6z8e', 'user_name': '丝袜御姐'},
                {'user_id': '3xufnbc9q5hw2fe', 'user_name': '初晴'},
                {'user_id': '3xu46dsqc5eyp6e', 'user_name': '甜甜'},
                {'user_id': '3xctqbbd2ac8q8a', 'user_name': '王语会'},
                {'user_id': '3xf9s8wg2dcftn4', 'user_name': '桃三七'},
                {'user_id': '3xvis9xti8tqvia', 'user_name': '张颖'},
                {'user_id': '3xm8rc5t669kkyq', 'user_name': '张颖'},
                {'user_id': '3x54t5dcfrqre29', 'user_name': '崔姑娘'},
                {'user_id': '3xdk533bx9ucbcm', 'user_name': '崔姑娘'},
                {'user_id': '3xc7247ny46uu79', 'user_name': '萝卜姐姐'},
                {'user_id': '3xmqwvgk2b9hj59', 'user_name': '萝卜姐姐'},
                {'user_id': '3xkujxe9bk8kztc', 'user_name': '小帅宝'},
                {'user_id': '3xgjx92etapgxkw', 'user_name': '舒芯'},
                {'user_id': '3x6ft58xxmap4di', 'user_name': '舒芯'},
                {'user_id': '3xhgsy7x5f3fqa4', 'user_name': '舒芯'},
                {'user_id': '3xviugk3e8kba8s', 'user_name': 'dd十九'},
                {'user_id': '3xfck2xthgzahr4', 'user_name': 'dd十九'},
                {'user_id': '3xnmwszp2zf2xti', 'user_name': '小妖月'},
                {'user_id': '3xgcpp59ydv9dg2', 'user_name': '恩玉'},
                {'user_id': '3xhdigukezbnq3m', 'user_name': '恩玉'},
                {'user_id': '3xyamugcjpeq2se', 'user_name': 'K小陌'},
                {'user_id': '3x58wxbvdhvyt49', 'user_name': 'K小陌'},
                {'user_id': '3x76giynxmb2whm', 'user_name': 'W98788'}
            ]

            user_idsss = []
            for iii in folspre:
                user_idsss.append(iii['user_id'])
            for jjj in fols_list:
                if jjj['user_id'] not in user_idsss:
                    folspre += jjj
                    # print('增加{}'.format(jjj))
            # fols_list = [
            #             ] + fols_list
            fols_list = folspre
        fols_list_len = len(fols_list)
        for item in fols_list:
            num = num + 1
            user_name = item['user_name']
            user_id = item['user_id']
            id_list.append(user_id)
            logger.info(f'{num}、 {user_name}：{user_id} >>> ID获取成功！！！')
            count += 1
            logger.info(f'第 [ {count} / {fols_list_len} ] 位关注：{user_id} 全部视频下载中...')
            # deal_author(user_id)
            deal_author_mul(user_id, user_name)
            logger.info(f'第 [ {count} / {fols_list_len} ] 位关注：{user_id} 全部视频下载完毕')
            logger.info('=' * 20)
            logger.info('')

    # logger.info(id_list)
    # print(id_list)
    # exit(0)
    return id_list


if __name__ == '__main__':
    proxies = {
        'http': 'http://192.168.55.12:1083',
        'https': 'http://192.168.55.12:1083',
    }
    webdids = ['web_01a6136e475af5dc13de8b38a0602e07']
    while True:
        kwaiutils = KwaiUtils()

        cookies = {
            'kpf': 'PC_WEB',
            # 'clientid': '4',
            'did': webdids[-1],
            'kpn': 'KUAISHOU_VISION',
        }
        cookies["did"] = webdids[-1]
        logger.info('req_cookies["did"] -> {}'.format(cookies['did']))

        cookies = {
            'did': 'web_7da1f457b92b4384b59fba0f38aad372',
            'didv': '1750685172000',
            'kwpsecproductname': 'PCLive',
            'kwfv1': 'PnGU+9+Y8008S+nH0U+0mjPf8fP08f+98f+nLlwnrIP9P9G98YPf8jPBQSweS0+nr9G0mD8B+fP/L98/qlPe4f8eql+A+D+/b0P9GF8/qAPe+D8fQ080qM8BGMweD7P9GFG08SPBLAwBGUP/mS+AQjGAPEwBLIP0Wh+AYSG0cA80Z=',
            'kpf': 'PC_WEB',
            'clientid': '3',
            'userId': '4871213682',
            'kuaishou.server.webday7_st': 'ChprdWFpc2hvdS5zZXJ2ZXIud2ViZGF5Ny5zdBKwAa4zBXtj2QNn5CTVwS0Sd_gtRK3WqQJEfrUmRnXBMtHIDfcrlqXjH7U8zQPXPM37u4LCrpl0OUENKf-EmFkkuZB7IxnTmsxjjLl7E7GoXFvztfWHJwo0jOkUsi6E1g3MT8NQ4k_7lr2EED0T1mnHIH8IniwDtqdZhdt3CZ5kZFxs6vk1dPBq4_dnp0FMdpKllquK1kx3TEwAhTRRWFA_dcNv99hh3sEUarZKi-q8lVzbGhKQHK981JaYVDFOSZbyEEWAlpMiIJYnjQ_Ecj5dwG-eS4Tb1a_R5kQSltolwDwhmxa5s14kKAUwAQ',
            'kuaishou.server.webday7_ph': '7fe355d937dbd75828f6b4961012dea0c68e',
            'kpn': 'KUAISHOU_VISION',
        }

        headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Origin': 'https://www.kuaishou.com',
            'Referer': 'https://www.kuaishou.com/profile/3xc7t2f9z3rste4',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'accept': '*/*',
            'content-type': 'application/json',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            # 'Cookie': 'did=web_7da1f457b92b4384b59fba0f38aad372; didv=1750685172000; kwpsecproductname=PCLive; kwfv1=PnGU+9+Y8008S+nH0U+0mjPf8fP08f+98f+nLlwnrIP9P9G98YPf8jPBQSweS0+nr9G0mD8B+fP/L98/qlPe4f8eql+A+D+/b0P9GF8/qAPe+D8fQ080qM8BGMweD7P9GFG08SPBLAwBGUP/mS+AQjGAPEwBLIP0Wh+AYSG0cA80Z=; kpf=PC_WEB; clientid=3; userId=4871213682; kuaishou.server.webday7_st=ChprdWFpc2hvdS5zZXJ2ZXIud2ViZGF5Ny5zdBKwAa4zBXtj2QNn5CTVwS0Sd_gtRK3WqQJEfrUmRnXBMtHIDfcrlqXjH7U8zQPXPM37u4LCrpl0OUENKf-EmFkkuZB7IxnTmsxjjLl7E7GoXFvztfWHJwo0jOkUsi6E1g3MT8NQ4k_7lr2EED0T1mnHIH8IniwDtqdZhdt3CZ5kZFxs6vk1dPBq4_dnp0FMdpKllquK1kx3TEwAhTRRWFA_dcNv99hh3sEUarZKi-q8lVzbGhKQHK981JaYVDFOSZbyEEWAlpMiIJYnjQ_Ecj5dwG-eS4Tb1a_R5kQSltolwDwhmxa5s14kKAUwAQ; kuaishou.server.webday7_ph=7fe355d937dbd75828f6b4961012dea0c68e; kpn=KUAISHOU_VISION',
        }
        req_cookies = cookies
        req_headers = headers
        # cookies = {
        #     'did': 'web_2077198417aebfbbc48949437bff73f5',
        #     'clientid': '3',
        #     'client_key': '65890b29',
        #     'kpf': 'PC_WEB',
        #     'didv': '1676202279000',
        #     'clientid': '3',
        #     'userId': '647446218',
        #     'kpn': 'KUAISHOU_VISION',
        #     'kuaishou.server.web_st': 'ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABpArzfhL5v0fhHsThQiHqHpnu441RiqdMl8cusWHwsY-nV3Et0ILI2rwId0Fdsbi_exZVrlaWEjJVtpbndpBC6a3kyVCknV85Qpu_B15e7NRnBj1EMF1MOxnl5JaiJEInVWRHpqEstNW8NaVpq6_OdUk6RYyRO4oY6QqcQl5LXQaIUp4qLxqtBpNxcAOYtmFbx8IZt9LCs73iFXXMz8twCxoStEyT9S95saEmiR8Dg-bb1DKRIiBu14GavZOT7OXFt4I90zLILyXfw6AassTXO9GF8cX4bigFMAE',
        #     'kuaishou.server.web_ph': '13cf6851dd6f4b5657fb0a9c23d8476f3b51',
        # }
        #
        # headers = {
        #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        #     'Connection': 'keep-alive',
        #     # 'Cookie': 'did=web_2077198417aebfbbc48949437bff73f5; clientid=3; client_key=65890b29; kpf=PC_WEB; didv=1676202279000; clientid=3; userId=647446218; kpn=KUAISHOU_VISION; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABpArzfhL5v0fhHsThQiHqHpnu441RiqdMl8cusWHwsY-nV3Et0ILI2rwId0Fdsbi_exZVrlaWEjJVtpbndpBC6a3kyVCknV85Qpu_B15e7NRnBj1EMF1MOxnl5JaiJEInVWRHpqEstNW8NaVpq6_OdUk6RYyRO4oY6QqcQl5LXQaIUp4qLxqtBpNxcAOYtmFbx8IZt9LCs73iFXXMz8twCxoStEyT9S95saEmiR8Dg-bb1DKRIiBu14GavZOT7OXFt4I90zLILyXfw6AassTXO9GF8cX4bigFMAE; kuaishou.server.web_ph=13cf6851dd6f4b5657fb0a9c23d8476f3b51',
        #     'DNT': '1',
        #     'Origin': 'https://www.kuaishou.com',
        #     'Referer': 'https://www.kuaishou.com/profile/3xhmcusb68pxwz4',
        #     'Sec-Fetch-Dest': 'empty',
        #     'Sec-Fetch-Mode': 'cors',
        #     'Sec-Fetch-Site': 'same-origin',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        #     'accept': '*/*',
        #     'content-type': 'application/json',
        #     'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        #     'sec-ch-ua-mobile': '?0',
        #     'sec-ch-ua-platform': '"Windows"',
        # }
        # cookies = {
        #     'did': 'web_9771250057fe45d6b1f6d8ecd27136bc',
        #     'didv': '1694920307000',
        #     'kpf': 'PC_WEB',
        #     'clientid': '3',
        #     'userId': '3740607963',
        #     'kpn': 'KUAISHOU_VISION',
        #     'kuaishou.server.web_st': 'ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABIGZQXQmSPeJe6WF6DKftAUeW5WPlxCIxkrfMt2z5TIaYMkyXT6cbP5C49JdM28_xTqmsmD114liqvn9lRdfWvB4M-H5XIMoTo-XSNBbFWijTCmGPsuskglnulQaayXpkb00Ymth9wweF2wdkgCwRN3Fuhntj_KVP15WiNetU1weQ7VH0LkhrTO1AAlB1Bwtnrm-X5RFljHGmBadG9RIeShoS_47WhL3lHryRDUsr7Z0BqLaUIiC7CzuE-m7dI47Qjjgxi1ppOr2bqwhhMBMHMzYIf5k57SgFMAE',
        #     'kuaishou.server.web_ph': '3b9068f1ae0f465b8fb4ee3585a138b3508f',
        # }

        # headers = {
        #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        #     'Connection': 'keep-alive',
        #     # 'Cookie': 'did=web_9771250057fe45d6b1f6d8ecd27136bc; didv=1694920307000; kpf=PC_WEB; clientid=3; userId=3740607963; kpn=KUAISHOU_VISION; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABIGZQXQmSPeJe6WF6DKftAUeW5WPlxCIxkrfMt2z5TIaYMkyXT6cbP5C49JdM28_xTqmsmD114liqvn9lRdfWvB4M-H5XIMoTo-XSNBbFWijTCmGPsuskglnulQaayXpkb00Ymth9wweF2wdkgCwRN3Fuhntj_KVP15WiNetU1weQ7VH0LkhrTO1AAlB1Bwtnrm-X5RFljHGmBadG9RIeShoS_47WhL3lHryRDUsr7Z0BqLaUIiC7CzuE-m7dI47Qjjgxi1ppOr2bqwhhMBMHMzYIf5k57SgFMAE; kuaishou.server.web_ph=3b9068f1ae0f465b8fb4ee3585a138b3508f',
        #     'DNT': '1',
        #     'Origin': 'https://www.kuaishou.com',
        #     'Referer': 'https://www.kuaishou.com/profile/3x2bmpj7cxab2xm',
        #     'Sec-Fetch-Dest': 'empty',
        #     'Sec-Fetch-Mode': 'cors',
        #     'Sec-Fetch-Site': 'same-origin',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76',
        #     'accept': '*/*',
        #     'content-type': 'application/json',
        #     'sec-ch-ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        #     'sec-ch-ua-mobile': '?0',
        #     'sec-ch-ua-platform': '"Windows"',
        # }
        follow_cookies = cookies
        follow_headers = headers

        quickmode = False
        # base_dir = os.path.abspath(os.path.dirname(__file__))
        base_dir = r'F:\video\kuaishou'

        # record_ok_path = os.path.join(base_dir, 'recordok')
        record_ok_path = base_dir
        print('保存小视频 -> {}'.format(record_ok_path))
        if not os.path.exists(record_ok_path):
            os.makedirs(record_ok_path)
        link = 'https://www.kuaishou.com/graphql'
        # pcursor这个变量的值开始必须为空，不用动他，它是换页的参数
        # selfid 是自己账号网址的最后面那一串 例如 https://www.kuaishou.com/profile/3xkfgnn9hkacbwc selfid 就是 3xkfgnn9hkacbwc

        selfids_ = ['3xnptsbuiecr89k',
                    '3x8na456zgqppcq',
                    ]
        # cks_ = [
        #     'clientid=3; client_key=65890b29; did={}; didv=1631014124364; userId=904333985; kpf=PC_WEB; kpn=KUAISHOU_VISION; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABst4n-l_8inWRqPP-HXAYMVl1SPwDhN0Ayg8lEF9wlQ5xHutaGS3ihCYBMb32dOBCPDs1_2oAXH5IJk6UVjqaOuTEia8CGXNJ-EI59aCJDeZY2GWLPDsyIXVRl0zxbkhzwkCGB-klqXBWXgffjk9Qa9cMmX6aRj2ZzUjZZ_h7YQuEkKM54KlV-Bq5frOwHrph8QRol6D4NNAEn1nnwZjmaRoS9XMBYg26NCtIxdOwhbHEY-u6IiAhU2_iXp6odDdPMGmb8WhXFwsZV03WvtTiNp_P13GBgCgFMAE; kuaishou.server.web_ph=377f279ef259702dafb0fc4fd13698755f75',
        #     'did={}; clientid=3; client_key=65890b29; userId=647446218; didv=1641916157000; kpf=PC_WEB; kpn=KUAISHOU_VISION; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABJ_YU1Sn_K3FS14a-u0j9U87czhTLw37uYwOvBgVif_8vJdL7tUIiXUvrMrKGubfoDsK7_nUzrV48xek37KrbkW4fhETyujA4BBywR6FCzBol7CeR6EVbHC3t05SP3qtgxM4tVV_iw2_iKTeTW8G7v315VDrBz2CILI5hL-rCehBTPpr0XxGnH3TvG_J9rpdezsze_RtTBd-8mRZ4y3gW3RoSWXnZQFypWC8Fi7687FtZGgfDIiC1PSnHtOK1JSfzyBKJJY-F_gCXjPiC3uUCUf_DselArygFMAE; kuaishou.server.web_ph=5a8ad46500fa0da79884fbfbc474cbf70289',
        # ]

        # selfid = '3x8na456zgqppcq'
        pcursor = ''
        # ck =''  引号中间填登录后的 Cookie 值
        # ck = 'clientid=3; client_key=65890b29; did=web_2077198417aebfbbc48949437bff73f5; didv=1631014124364; userId=904333985; kpf=PC_WEB; kpn=KUAISHOU_VISION; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABst4n-l_8inWRqPP-HXAYMVl1SPwDhN0Ayg8lEF9wlQ5xHutaGS3ihCYBMb32dOBCPDs1_2oAXH5IJk6UVjqaOuTEia8CGXNJ-EI59aCJDeZY2GWLPDsyIXVRl0zxbkhzwkCGB-klqXBWXgffjk9Qa9cMmX6aRj2ZzUjZZ_h7YQuEkKM54KlV-Bq5frOwHrph8QRol6D4NNAEn1nnwZjmaRoS9XMBYg26NCtIxdOwhbHEY-u6IiAhU2_iXp6odDdPMGmb8WhXFwsZV03WvtTiNp_P13GBgCgFMAE; kuaishou.server.web_ph=377f279ef259702dafb0fc4fd13698755f75'
        # ua = '' 引号中间填 User-Agent
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
        # save(link, pcursor, ck, ua, selfid)
        #
        debugMode = False
        selfid_idx = 0
        for selfid_idx in range(len(selfids_)):
            pcursor = ''
            selfid = selfids_[selfid_idx]
            # cktmp = cks_[selfid_idx]
            ua = getUa()
            ck = ''
            # req_data_cookies_global = getCookies()
            # did_global = req_data_cookies_global.get('did')
            # ck = cktmp.format(did_global)
            # ck = cktmp
            idlist = get_all_ids(link, pcursor, ck, ua, selfid)
        break
        sleep_dis(1800)
