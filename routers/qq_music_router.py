# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/19 : 16:54
import io
from typing import List

from fastapi import APIRouter, Response
from starlette.responses import RedirectResponse, StreamingResponse

from models.music import Song, SongUrls, SearchedSong, AudioResponse
from api.qqmusic import QQMusicClient
from tools import get_audio_response

router = APIRouter(
    prefix="/qqmusic",
    tags=["QQ Music"]
)

client = QQMusicClient()


@router.get("/")
def qq_music_root(logged_in: bool):
    return f"欢迎使用QQ音乐API，当前登录状态：{logged_in}"


@router.get("/login")
def login(new: int = 0):
    if new != 0:
        img = client.login()
        return StreamingResponse(io.BytesIO(img), media_type="image/jpeg")
    if client.logged_in:
        return RedirectResponse(url="/qqmusic?logged_in=True")
    else:
        img = client.login()
        return StreamingResponse(io.BytesIO(img), media_type="image/jpeg")


@router.get("/login/check")
def login_check():
    if client.logged_in:
        return "true"
    else:
        return "false"


@router.get("/songs/search", response_model=AudioResponse)
def song_search(query: str, num: int = 1):
    songs = client.search(query, num)
    if songs is not None:
        return get_audio_response(code=0, msg='successes!', data=songs)
    else:
        return get_audio_response(code=111, msg='没有登录xd!', data=songs)


@router.get("/songs", response_model=AudioResponse)
def song_get(song_mid: str):
    """
    Get song by song id
    :param song_mid: the ids of specific songs
    :return: data of song
    """
    song_mid = song_mid.split(',')
    play_urls = client.get_play_url(song_mid=song_mid)
    if play_urls is not None:
        return get_audio_response(code=0, msg='successes!', data=play_urls)
    else:
        return get_audio_response(code=-1, msg='失败!', data=play_urls)


@router.get("/playlist", response_model=AudioResponse)
def playlist_get(diss_id: int):
    playlist = client.get_playlist(diss_id=diss_id)
    if playlist is not None:
        return get_audio_response(code=0, msg='successes!', data=playlist)
    else:
        return get_audio_response(code=-1, msg='失败!', data=playlist)
