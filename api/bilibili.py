# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/26 : 13:23

"""
bilibili音频获取模块
"""
import asyncio
import json
import random
import re
import aiohttp
import requests
from datetime import datetime
from models.music import AudioBilibili, AudioBilibiliList

header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
}


class BilibiliClient:
    def __init__(self):
        self.session = requests.Session()
        self.cookie_jar = aiohttp.CookieJar(unsafe=True)

    async def get_audio_url(self, bvid: str):
        audio_list = AudioBilibiliList()
        try:
            first_audio, pages = await self._try_to_get_audio_url(bvid)
            audio_list.pages = pages
            audio_list.list.append(first_audio)
            if pages > 1:
                tasks = [self._try_to_get_audio_url(bvid, i) for i in range(2, pages + 1)]
                futures = await asyncio.gather(*tasks)
                audio_list.list.extend([future[0] for future in futures])
            return audio_list
        except Exception as e:
            print(e)
            return None

    async def _try_to_get_audio_url(self, bvid: str, p: int = 1):
        url = f"https://www.bilibili.com/video/{bvid}/"
        param = {
            "p": p,
            "vd_source": "a97ce8f6ce42e3ca9a7f2426d0a483f0"
        }
        async with aiohttp.ClientSession(cookie_jar=self.cookie_jar) as session:
            async with session.get(url, params=param, headers=header) as response:
                # 等待响应时间
                await asyncio.sleep(2)
                text = await response.text()
                if response.status == 200:
                    try:
                        pattern_info = r'<script>window.__INITIAL_STATE__=(.*?);\(function'
                        info_data = re.findall(pattern_info, text, re.S)[0]
                        pattern_audio = r'<script>window.__playinfo__=(.*?)</script>'
                        audio_data = re.findall(pattern_audio, text, re.S)[0]
                        info_data = json.loads(info_data)
                        audio = {
                            'audio_url': json.loads(audio_data)['data'].get('dash').get('audio')[0].get('base_url'),
                            'aid': info_data.get('aid'),
                            'bvid': bvid,
                            'cid': info_data.get('videoData').get('pages')[p - 1].get('cid'),
                            'title': info_data.get('videoData').get('title'),
                            'part': info_data.get('videoData').get('pages')[p - 1].get('part'),
                            'desc': info_data.get('videoData').get('desc'),
                            'time_public': datetime.fromtimestamp(info_data.get('videoData').get('pubdate')).strftime(
                                '%Y-%m-%d'),
                            'owner_id': info_data.get('upData').get('mid'),
                            'owner_name': info_data.get('upData').get('name'),
                            'face': info_data.get('upData').get('face'),
                            'pic_url': info_data.get('videoData').get('pic')
                        }

                        pages = info_data.get('videoData').get('videos')
                        return AudioBilibili(**audio), pages
                    except Exception as e:
                        print(f"{e}: something wrong in _try_to_get_audio_url")
                else:
                    return None


if __name__ == '__main__':
    client = BilibiliClient()
    print(client.get_audio_url("BV18m411271p"))
    # print(client.get_audio_url("BV1SA41157Nt"))
    # https://xy111x21x155x92xy.mcdn.bilivideo.cn:4483/upgcxcode/74/16/157261674/157261674-1-30280.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1714197103&gen=playurlv2&os=mcdn&oi=1863459470&trid=00002dea348a23e54e00b2eee6fd6c2a9403u&mid=0&platform=pc&upsig=1d0a35cd0f76b55004f66faf52ed82c0&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=16000546&bvc=vod&nettype=0&orderid=0,3&buvid=BBA99D5B-0FED-80A6-776D-4CA4622A311903462infoc&build=0&f=u_0_0&agrr=0&bw=16572&logo=A0008000
    # https://xy111x21x155x92xy.mcdn.bilivideo.cn:4483/upgcxcode/74/16/157261674/157261674-1-30280.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1714197172&gen=playurlv2&os=mcdn&oi=1863459527&trid=0000fb53d002ea9c4d65aabd93905462898eu&mid=0&platform=pc&upsig=4bd11a820bb2992e54bb4f856745c0cd&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=16000546&bvc=vod&nettype=0&orderid=0,3&buvid=BBA99D5B-0FED-80A6-776D-4CA4622A311903462infoc&build=0&f=u_0_0&agrr=0&bw=16572&logo=A0008000
