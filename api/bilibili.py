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
import time

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

    async def get_audio(self, bvid: str):
        try:
            audios = await self._get_audio_list(bvid)
            print(audios)
            if audios is not None:
                tasks = [self._get_audio_play_url(audio) for audio in audios.list]
                futures = await asyncio.gather(*tasks)
                audios.list = [future for future in futures if future is not None]
                return audios
        except Exception as e:
            print(e)
            return None

    async def _get_audio_list(self, bvid: str):
        url = f"https://www.bilibili.com/video/{bvid}/"
        async with aiohttp.ClientSession(cookie_jar=self.cookie_jar) as session:
            async with session.get(url, headers=header) as response:
                # 等待响应时间
                text = await response.text()
                if response.status == 200:
                    try:
                        pattern_info = r'<script>window.__INITIAL_STATE__=(.*?);\(function'
                        info_data = re.findall(pattern_info, text, re.S)[0]
                        info_data = json.loads(info_data)
                        pages = info_data.get('videoData').get('pages')
                        audio = {
                            'aid': info_data.get('aid'),
                            'bvid': info_data.get('bvid'),
                            'title': info_data.get('videoData').get('title'),
                            'desc': info_data.get('videoData').get('desc'),
                            'time_public': datetime.fromtimestamp(info_data.get('videoData').get('pubdate')).strftime(
                                '%Y-%m-%d'),
                            'owner_id': info_data.get('upData').get('mid'),
                            'owner_name': info_data.get('upData').get('name'),
                            'face': info_data.get('upData').get('face'),
                            'pic_url': info_data.get('videoData').get('pic')
                        }
                        audio_list = self._list_audios(pages=pages, audio_basic=audio)
                        return audio_list
                    except Exception as e:
                        print(f"{e}: something wrong in _get_audio_list")
                else:
                    return None

    def _list_audios(self, pages, audio_basic):
        """列出暂时没有音频链接的音频"""
        audios = [self._update_audio(audio_basic, {'cid': page.get('cid'), 'part': page.get('part'), 'audio_url': None})
                  for page in pages]
        pages = len(audios)
        audio_list = {
            "list": [AudioBilibili(**audio) for audio in audios],
            "pages": pages
        }
        return AudioBilibiliList(**audio_list)

    @staticmethod
    def _update_audio(audio: dict, new: dict):
        """更新音频信息"""
        audio.update(new)
        return audio

    async def _get_audio_play_url(self, audio: AudioBilibili):
        aid, bvid, cid = audio.aid, audio.bvid, audio.cid
        url = "https://api.bilibili.com/x/player/playurl"
        param = {
            "avid": aid,
            "cid": cid,
            "bvid": bvid,
            "qn": 80,
            "fnver": 0,
            "fnval": 4048,
            "fourk": 1,
            "gaia_source": "",
            "from_client": "BROWSER",
            "need_fragment": "false",
            "is_main_page": "true",
            "isGaiaAvoided": "true",
            "voice_balance": 1,
            "web_location": "1315873",
            "session": "d5413e188ff2be3b887678cf8d208b91",
            "w_rid": "120f1404c2f18eaab0ecd7bd1c859748",
            "wts": int(time.time())
        }
        async with aiohttp.ClientSession(cookie_jar=self.cookie_jar) as session:
            async with session.get(url, params=param, headers=header) as response:
                # await asyncio.sleep(3)
                try:
                    data = await response.json()
                    audio_url = data.get('data').get('dash').get('audio')[0].get('baseUrl')
                    audio.audio_url = audio_url
                    return audio
                except Exception as e:
                    print(f"{e}: Something wrong with getting play urls")
                    return None


if __name__ == '__main__':
    client = BilibiliClient()
    print(client.get_audio("BV18m411271p"))
    # print(client.get_audio_url("BV1SA41157Nt"))
