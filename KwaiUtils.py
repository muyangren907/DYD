# -*- coding: utf-8 -*-
# @Time    : 2023/3/3 2:00
# @Author  : muyangren907
# @Email   : myr907097904@gmail.com
# @File    : KwaiUtils.py
# @Software: PyCharm
import re
import time
import requests
import json

class KwaiUtils:
    def __init__(self):
        self.author = 'muyangren0907'

    def get_video_info(self,video_id, author_id):
        '''
            video_id = item['photo']['id']
            video_name = item['photo']['caption']
            video_url = item['photo']['photoUrl']
            video_timestamp = item['photo']['timestamp']
            video_uptime = timestamp2strtime(video_timestamp)
            author = item['author']['name']
            author = strfomat(author)[:15]
            author_id = item['author']['id']
            video_name = strfomat(video_name)[:20]
        '''
        cookies = {
            'kpf': 'PC_WEB',
            'clientid': '3',
            'did': 'web_6f7ff23a1166c078e6965ca5a9e4ac79',
            '_did' : 'web_418204116C822EB0',
            # 'did': '{}'.format(self.gen_did()),
            # 'userId': '3323491049',
            'kpn': 'KUAISHOU_VISION',
            # 'kuaishou.server.web_st': 'ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABC2vbJlE5PMLXjOSjh5bRo1RrXfb0SwUDRrFt0651xxybmsPv6I02LaeTKDB6s_6JtFvIf8ShkWPleNGH5UkJelLB-BmbczVxGRmVcKeykPREIkgDKaEsl0-1-q4Md7Mi3wYVtbw5fraTl20Gf2g2O3YW8KLsxaADlXN3rosUG-f8J16qTlkwD_m_nt1FsxvRCnFeAHdmnNHZ3zOZpqpfCRoS7YoRGiN2PM_7zCD1Dj9m5oYoIiCFReNBBr7x2vYNI_x4HUKixCOPjo1nyOItkVMx8zOoQigFMAE',
            # 'kuaishou.server.web_ph': '06a0282b97bcb7b88643f906c0ab0ce51cff',
        }

        headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 'Cookie': 'kpf=PC_WEB; clientid=3; did=web_1055ce6d401b9c6d4964524c1f8013a5; userId=3323491049; kpn=KUAISHOU_VISION; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABC2vbJlE5PMLXjOSjh5bRo1RrXfb0SwUDRrFt0651xxybmsPv6I02LaeTKDB6s_6JtFvIf8ShkWPleNGH5UkJelLB-BmbczVxGRmVcKeykPREIkgDKaEsl0-1-q4Md7Mi3wYVtbw5fraTl20Gf2g2O3YW8KLsxaADlXN3rosUG-f8J16qTlkwD_m_nt1FsxvRCnFeAHdmnNHZ3zOZpqpfCRoS7YoRGiN2PM_7zCD1Dj9m5oYoIiCFReNBBr7x2vYNI_x4HUKixCOPjo1nyOItkVMx8zOoQigFMAE; kuaishou.server.web_ph=06a0282b97bcb7b88643f906c0ab0ce51cff',
            'DNT': '1',
            'Origin': 'https://www.kuaishou.com',
            'Referer': 'https://www.kuaishou.com/{}'.format(video_id),
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'accept': '*/*',
            'content-type': 'application/json',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        # video_id = '3xheap9sxidiqii'
        # req_cookies = cookies
        # req_headers = headers
        # page = ''
        while True:
            try:
                # 'https://www.kuaishou.com/short-video/3xyvdmx8gwqpm2e?authorId=3x5mcxa5hc8wx7e&streamSource=profile&area=profilexxnull'
                response = requests.get('https://www.kuaishou.com/short-video/{}?authorId={}&streamSource=profile&area=profilexxnull'.format(video_id,author_id), headers=headers,
                                        cookies=cookies)
                print(response.text)
                restext = response.text
                spos = restext.index('<script>window.__APOLLO_STATE__=') + len('<script>window.__APOLLO_STATE__=')
                epos = restext[spos:].index('};') + 1
                jsonstr = restext[spos:spos + epos]
                print(jsonstr)
                resjson = json.loads(jsonstr)
                # JSON.defaultClient.VisionVideoDetailPhoto:3xin87pmu3dru2u

                defaultClient = resjson['defaultClient']
                print(defaultClient)
                # for iii in defaultClient:
                #     print('{}\t{}'.format(iii, defaultClient[iii]))
                visionVideoDetailPhoto = defaultClient['VisionVideoDetailPhoto:{}'.format(video_id)]
                break
            except Exception as e:
                print(e)

        print(visionVideoDetailPhoto)
        # caption = visionVideoDetailPhoto['caption']
        # video_timestamp = visionVideoDetailPhoto['timestamp']
        # photoUrl = visionVideoDetailPhoto['photoUrl']

        # video_id = video_id
        video_name = visionVideoDetailPhoto['caption']
        video_url = visionVideoDetailPhoto['photoUrl']
        video_timestamp = visionVideoDetailPhoto['timestamp']
        video_uptime = self.timestamp2strtime(video_timestamp)
        vvdaidx = ''
        for iii in defaultClient:
            if 'VisionVideoDetailAuthor' in iii:
                vvdaidx = iii
                break
        visionVideoDetailAuthor = defaultClient[vvdaidx]
        author = visionVideoDetailAuthor['name']
        author = self.strfomat(author)[:15]
        author_id = visionVideoDetailAuthor['id']
        video_name = self.strfomat(video_name)[:20]

        author_dic = {}
        author_dic['author'] = author
        author_dic['author_id'] = author_id
        video_dic = {}
        video_dic['video_id'] = video_id
        video_dic['video_name'] = video_name
        video_dic['video_uptime'] = video_uptime
        video_dic['video_timestamp'] = video_timestamp
        video_dic['video_url'] = video_url
        ret_dic = {}
        ret_dic['author'] = author_dic
        ret_dic['video'] = video_dic
        print(ret_dic)
        return ret_dic

        # print('{}\n{}\n{}'.format(caption, timestamp, photoUrl))

    def gen_did(self):
        cookies = {
            '_did': 'web_418204116C822EB0',
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 'Cookie': '_did=web_418204116C822EB0',
            'DNT': '1',
            'Origin': 'https://live.kuaishou.com',
            'Referer': 'https://live.kuaishou.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        data = {
            'sid': 'kuaishou.live.web',
        }

        import requests
        response = requests.post('https://id.kuaishou.com/pass/kuaishou/login/passToken', cookies=cookies,
                                 headers=headers, data=data)
        # print(response.text)
        coo = response.headers['Set-Cookie']

        coos = coo.split(';')
        didstr = ''
        for iii in coos:
            if 'did=' in iii:
                didstr = iii.replace('did=', '')
                break
        print(didstr)

    def strfomat(self, str_in):
        sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", str_in)
        return sub_str

    def sleep_dis(self, sleep_time):
        for i in range(sleep_time, -1, -1):
            print('休眠 %5s s' % i, end='\r')
            time.sleep(1)
