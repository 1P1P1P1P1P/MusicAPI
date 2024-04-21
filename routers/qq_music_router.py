# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/19 : 16:54
from typing import List

from fastapi import APIRouter, Response
from starlette.responses import RedirectResponse, StreamingResponse

from models.music import Song, SongUrls, SearchedSong
from api.qqmusic import QQMusicClient

router = APIRouter(
    prefix="/qqmusic",
    tags=["QQ Music"]
)

client = QQMusicClient()


@router.get("/")
def qq_music_root(logged_in: bool):
    login_info = {"logged_in": logged_in}
    return login_info


@router.get("/login")
def login(new: int = 0):
    if new != 0:
        img = client.login()
        return StreamingResponse(img)
    if client.logged_in:
        return RedirectResponse(url="/qqmusic?logged_in=True")
    else:
        img = client.login()
        return StreamingResponse(img)

@router.get("/login/check")
def login_check():
    if client.logged_in:
        return "true"
    else:
        return "false"

@router.get("/songs/search", response_model=SearchedSong)
def song_search(query: str, num: int = 1):
    songs = client.search(query, num)
    print(songs)
    if songs[0].mid == '':
        print("可能还未登录")
    results = SearchedSong(**{"songs": songs, "num": len(songs)})
    return results


@router.get("/songs/url", response_model=SongUrls)
def song_get(song_mid: str):
    """
    Get song by song id
    :param song_mid: the ids of specific songs
    :return: data of song
    """
    song_mid = song_mid.split(',')
    play_urls = client.get_play_url(song_mid=song_mid)
    return play_urls

