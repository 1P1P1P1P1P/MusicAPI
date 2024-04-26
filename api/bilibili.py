# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/26 : 13:23

"""
bilibili音频获取模块
"""
import json
import re
import requests
from datetime import datetime
from models.music import AudioBilibili

header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
}


class BilibiliClient:
    def __init__(self):
        self.session = requests.Session()

    def get_audio_url(self, bvid: str):
        url = f"https://www.bilibili.com/video/{bvid}/"
        response = self.session.get(url, headers=header)
        if response.status_code == 200:
            pattern_audio = r'<script>window.__playinfo__=(.*?)</script>'
            audio_data = re.findall(pattern_audio, response.content.decode('utf-8'), re.S)[0]
            pattern_info = r'<script>window.__INITIAL_STATE__=(.*?);\(function'
            info_data = re.findall(pattern_info, response.content.decode('utf-8'), re.S)[0]
            info_data = json.loads(info_data)
            audio = {
                'audio_url': json.loads(audio_data)['data'].get('dash').get('audio')[0].get('base_url'),
                'aid': info_data.get('aid'),
                'bvid': bvid,
                'title': info_data.get('videoData').get('title'),
                'desc': info_data.get('videoData').get('desc'),
                'time_public': datetime.fromtimestamp(info_data.get('videoData').get('pubdate')).strftime('%Y-%m-%d'),
                'owner_id': info_data.get('upData').get('mid'),
                'owner_name': info_data.get('upData').get('name'),
                'face': info_data.get('upData').get('face'),
                'pic_url': info_data.get('videoData').get('pic')
            }
            return AudioBilibili(**audio)
        else:
            return None


if __name__ == '__main__':
    client = BilibiliClient()
    client.get_audio_url("BV1KV411x7Kb")
