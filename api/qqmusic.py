# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/18 : 15:02
import asyncio
import json
import random
import re
import threading
import time
from io import BytesIO
from typing import List
import requests
import requests.utils
import numpy as np
import execjs
from models.music import Song, SongUrls, PlayList, Tag
import matplotlib.pyplot as plt
from api.api_errors import NotLoggedIn

with open('api/js/qqmain.js', 'r', encoding='utf-8') as f:
    js = f.read()


def start_loop(loop, task):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(task)


def g_tk(skey):
    temp = 5381
    length = len(skey)
    for i in range(length):
        if i < length:
            temp += (temp << 5) + ord(skey[i])
    return 2147483647 & temp


def hash33(s):
    """
    实现hash33加密算法，用于login
    :param s: 获得的qrsig来自cookies
    :return: hash33后的值
    """
    e = 0
    for i in range(len(s)):
        e += (e << 5) + ord(s[i])
    return 2147483647 & e


def get_sign(form):
    """
    获取QQMusic sign参数
    :param form: 表单数据，注意对于中文要进行url编码
    :return: Sign的值
    """
    sign = execjs.compile(js).call('get_sign', form)
    return sign


def get_search_id(search_type=3):
    """
    获取search id
    :param search_type: search 的类型
    :return: 获得的search id
    """
    search_id = execjs.compile(js).call('get_search_id', search_type)
    return search_id


def get_guid():
    guid = execjs.compile(js).call('get_guid')
    return guid


header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
}


class QQMusicClient:
    """QQ音乐API"""

    def __init__(self):
        self.t = None
        self.session = requests.Session()
        self.session.headers.update(**header)
        self.logged_in = False
        self.ptqr_token = None
        self.uin = None
        self._get_login_cookies()

    def _get_login_cookies(self):
        try:
            with open('cookie.json', 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            self.session.cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
            self.uin = self.session.cookies.get('uin', None)
            if self.uin is None:
                raise NotLoggedIn(code=111, msg="没有用户uin, 可能未登录")
            self.logged_in = True
        except NotLoggedIn as e:
            print(e)
        except FileNotFoundError:
            print("你需要登录")

    def _check_task(self):
        new_loop = asyncio.new_event_loop()
        coroutine = self._check_login_loop()
        self.t = threading.Thread(target=start_loop, args=(new_loop, coroutine,))

    def login(self):
        """登录"""
        self.logged_in = False
        self._check_task()
        self.session.cookies.clear()
        img = self._get_login_qr()
        self.t.start()
        # 测试时用于展示二维码
        # plt.imshow(plt.imread(BytesIO(img)))
        # plt.show()
        return img

    async def _check_login_loop(self):
        check_start_time = time.time()
        try:
            while 1:
                if self.ptqr_token is None:
                    await asyncio.sleep(1)
                    continue
                res = self._check_login(self.ptqr_token)
                res = re.search(r"\((.*?)\)", res).group(1)
                res = res.replace("'", "")
                res_list = res.split(",")
                print(res_list[4])
                if res_list[0] == "0":
                    self.logged_in = True
                    redirect_url = res_list[2]
                    self._get_all_cookies(redirect_url)
                    self.uin = self.session.cookies.get('uin', None)
                    with open("cookie.json", 'w') as f:
                        json.dump(self.session.cookies.get_dict(), f)
                    break
                if time.time() - check_start_time > 60:
                    raise TimeoutError()
        except TimeoutError:
            print("超时！请重新尝试！")
            self.logged_in = False

    def _get_login_qr(self) -> bytes:
        """login的辅助函数，用于获得二维码"""
        qr_url = "https://ssl.ptlogin2.qq.com/ptqrshow"
        qr_param = {
            "appid": "716027609",
            "e": "2",
            "l": "M",
            "s": "3",
            "d": "72",
            "v": "4",
            "t": np.random.random(),
            "daid": "383",
            "pt_3rd_aid": "100497308",
            "u1": "https://graph.qq.com/oauth2.0/login_jump"
        }
        response = self.session.get(qr_url, params=qr_param)
        img = response.content
        self.ptqr_token = hash33(self.session.cookies.get("qrsig"))
        return img

    def _check_login(self, ptqr_token) -> str:
        """
        判断二维码有效性
        :param ptqr_token: hash33后的qrsig值
        :return: 得到的response内容
        """
        check_url = "https://ssl.ptlogin2.qq.com/ptqrlogin"
        check_param = {
            "u1": "https://graph.qq.com/oauth2.0/login_jump",
            "ptqrtoken": ptqr_token,
            "ptredirect": "0",
            "h": "1",
            "t": "1",
            "g": "1",
            "from_ui": "1",
            "ptlang": "2052",
            "action": "0-0-" + str(int(time.time() * 1000)),
            "js_ver": "24032716",
            "js_type": "1",
            "login_sig": "",
            "pt_uistyle": "40",
            "aid": "716027609",
            "daid": "383",
            "pt_3rd_aid": "100497308",
            "o1vId": "8bc0d8b5167d05f33cdbbd138dc34379",
            "pt_js_version": "v1.48.2"
        }
        response = self.session.get(check_url, params=check_param)
        time.sleep(3 * random.random())
        return response.text

    def _get_all_cookies(self, redirect_url):
        self.session.get(redirect_url)
        form_auth = {
            "response_type": "code",
            "client_id": 100497308,
            "redirect_uri": "https://y.qq.com/portal/wx_redirect.html?login_type=1&surl=https://y.qq.com/",
            "scope": "get_user_info,get_app_friends",
            "state": "state",
            "switch": "",
            "from_ptlogin": 1,
            "src": 1,
            "update_auth": 1,
            "openapi": "1010_1030",
            "g_tk": g_tk(self.session.cookies.get('qqmusic_key', "")),
            "auth_time": int(time.time() * 1000),
            "ui": "B4A0D877-6B02-4038-B5DE-9626663AA3FE"
        }
        url_auth = "https://graph.qq.com/oauth2.0/authorize"
        res_auth = self.session.post(url=url_auth, data=form_auth)
        redict_url_2 = res_auth.url
        code = re.search(r"code=(.*?)&", redict_url_2).group(1)
        final_cookie_form = json.dumps(self._get_cookies_form(code=code)).encode("utf-8")
        final_cookie_url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        self.session.post(final_cookie_url, data=final_cookie_form)
        # print(self.session.cookies.get_dict())

    def search(self, query: str, query_type: int = 3, num: int = 1) -> List[Song]:
        """
        搜索部分
        :param num: 查询的返回数量(目前没有适配超过10的数量)
        :param query: 搜索请求内容
        :param query_type: 搜索请求的类型, 默认是搜索音乐
        :return: 返回搜索的内容
        """
        try:
            if self.uin is None:
                raise NotLoggedIn(code=111, msg="没有用户uin, 可能未登录")
        except NotLoggedIn as e:
            print(e)
        except Exception as e:
            error_song = {
                'id': 0,
                'mid': '',
                'name': '',
                'desc': '',
            }
            return [Song(**error_song)]
        search_url = "https://u6.y.qq.com/cgi-bin/musics.fcg"
        form = self._get_basic_form()
        req_form = self._get_req_form(req_type='search')
        form.update(req_form)
        form["req_1"]['param']['query'] = query
        form["req_1"]['param']['searchid'] = get_search_id(query_type)
        form_str = json.dumps(form, separators=(',', ':'), ensure_ascii=False)
        param = {
            "_": str(int(time.time() * 1000)),
            "sign": get_sign(form=form_str)
        }
        # print(f"Searching for query: {query}")
        try:
            res = self.session.post(search_url, params=param, data=form_str.encode('utf-8'))
            all_data = res.json()

            if all_data.get('code') == 0:
                req = all_data.get('req_1')
                data = req.get('data').get('body').get('song')['list']
                songs = [self._get_song(song) for song in data]
                print(songs)
                return songs
            else:
                raise Exception(f"ERROR CODE: {all_data.get('code')}")
        except requests.exceptions.JSONDecodeError as e:
            print("Wrong json")
        except Exception as e:
            print(e)

    def get_play_url(self, song_mid) -> SongUrls:
        url = "https://u6.y.qq.com/cgi-bin/musics.fcg"
        form = self._get_basic_form()
        req_form = self._get_req_form(req_type='getVkey')
        form.update(req_form)
        form['req_1']['param']['songmid'].extend(song_mid)
        form['req_1']['param']['songtype'] = [0 for _ in song_mid]
        form['req_1']['param']['guid'] = get_guid()
        form_str = json.dumps(form, separators=(',', ':'))
        param = {
            "_": str(int(time.time() * 1000)),
            "sign": get_sign(form=form_str)
        }
        try:
            res = self.session.post(url, params=param, data=form_str)
            midurlinfos = res.json().get("req_1").get('data').get('midurlinfo')
            purls = [x.get('purl') for x in midurlinfos]
            sip_0 = "http://ws.stream.qqmusic.qq.com/"
            # sip_1 = "http://isure.stream.qqmusic.qq.com/"
            urls_dict = {"urls": [sip_0 + x for x in purls]}
            song_urls = SongUrls(**urls_dict)
            return song_urls
        except Exception as e:
            print("Something went wrong: Care for the Mid and your input info:")

    def get_playlist(self, diss_id: int) -> PlayList:
        song_collected = 0
        url = "https://u6.y.qq.com/cgi-bin/musics.fcg"
        form = self._get_basic_form()
        req_form = self._get_req_form(req_type='getPlaylist')
        form.update(req_form)
        form['req_1']['param']['disstid'] = diss_id
        playlist = PlayList()
        while 1:
            form_str = self._get_playlist_helper(form, song_collected)
            param = {
                "_": str(int(time.time() * 1000)),
                "sign": get_sign(form=form_str)
            }
            try:
                res = self.session.post(url, params=param, data=form_str)
                data = res.json().get("req_1").get('data')
                dir_info = data.get("dirinfo")
                if song_collected == 0:
                    playlist.diss_id = dir_info.get('id')
                    playlist.song_num = dir_info.get('songnum')
                    playlist.desc = dir_info.get('desc')
                    playlist.pic_url = dir_info.get('picurl')
                    if type(tags := dir_info.get('tags')) is list:
                        playlist.tag = [Tag(**t) for t in tags]
                song_list = data.get("songlist")
                playlist.song_list.extend([self._get_song(song) for song in song_list])
                if not song_list:
                    break
            except Exception as e:
                print(e)
                print("Something went wrong: Care for the playlist id and your input info")
                break
            else:
                song_collected += len(song_list)
        return playlist

    def _get_song(self, song) -> Song:
        song_data = {
            "id": song.get("id"),
            "mid": song.get("mid"),
            "name": song.get("name"),
            "desc": song.get("desc", ""),
            "album_mid": song.get("album").get("mid"),
            "album_name": song.get("album").get("name"),
            "time_public": song.get("time_public"),
        }
        if song_data.get('album_mid') != '':
            pic_url = f"https://y.qq.com/music/photo_new/T002R300x300M000{song_data.get('album_mid')}.jpg?max_age=2592000"
        else:
            pic_url = f"https://y.qq.com/music/photo_new/T062R300x300M000{song_data.get('mid')}.jpg?max_age=2592000"
        song_data['pic_url'] = pic_url
        if type(song.get('singer')) is list:
            song_data['singer_mid'] = '|'.join([x.get('mid') for x in song.get('singer')])
            song_data['singer_name'] = '|'.join([x.get('name') for x in song.get('singer')])
        else:
            song_data['singer_mid'] = song.get('singer').get('mid')
            song_data['singer_name'] = song.get('singer').get('name')
        return Song(**song_data)

    def _get_playlist_helper(self, form, song_collected: int):
        form['req_1']['param']['song_begin'] = song_collected
        form_str = json.dumps(form, separators=(',', ':'))
        return form_str

    def _get_basic_form(self):
        basic_form = {
            "comm": {
                "cv": 4747474,
                "ct": 24,
                "format": "json",
                "inCharset": "utf-8",
                "outCharset": "utf-8",
                "notice": 0,
                "platform": "yqq.json",
                "needNewCode": 1,
                "uin": int(self.uin),
                "g_tk_new_20200303": g_tk(self.session.cookies.get('qqmusic_key', "")),
                "g_tk": g_tk(self.session.cookies.get('qqmusic_key', ""))
            }
        }
        return basic_form

    def _get_req_form(self, req_type):
        all_rep_form = {
            'search': {
                "req_1": {
                    "method": "DoSearchForQQMusicDesktop",
                    "module": "music.search.SearchCgiService",
                    "param": {
                        "remoteplace": "txt.yqq.top",
                        "searchid": None,
                        "search_type": 0,
                        "query": None,
                        "page_num": 1,
                        "num_per_page": 10
                    }
                }
            },
            "getVkey": {
                "req_1": {
                    "module": "vkey.GetVkeyServer",
                    "method": "CgiGetVkey",
                    "param": {
                        "guid": None,
                        "songmid": [],
                        "songtype": [],
                        "uin": self.uin,
                        "loginflag": 1,
                        "platform": "20"
                    }
                }
            },
            "getPlaylist": {
                "req_1": {
                    "module": "music.srfDissInfo.aiDissInfo",
                    "method": "uniform_get_Dissinfo",
                    "param": {
                        "disstid": 0,
                        "userinfo": 1,
                        "tag": 1,
                        "orderlist": 1,
                        "song_begin": 0,
                        "song_num": 10,
                        "onlysonglist": 0,
                        "enc_host_uin": ""
                    }
                }
            }
        }
        return all_rep_form[req_type]

    def _get_cookies_form(self, code):
        form = {
            "comm": {
                "g_tk": g_tk(self.session.cookies.get('qqmusic_key', "")),
                "platform": "yqq",
                "ct": 24,
                "cv": 0
            },
            "req": {
                "module": "QQConnectLogin.LoginServer",
                "method": "QQLogin",
                "param": {
                    "code": code
                }
            }
        }
        return form


if __name__ == '__main__':
    client = QQMusicClient()
    # client.login()
    # client.search("游园会")
    # client.get_play_url(song_mid=["003aWhog3a86Ro"])
    client.get_playlist(diss_id=3256986457)
