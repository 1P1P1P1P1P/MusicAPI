# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/17 : 18:31
from enum import Enum
from typing import List

from pydantic import BaseModel


class SourceName(str, Enum):
    """
    音乐来源的名称
    """
    neteasecloud = "neteasecloud"
    qqmusic = "qqmusic"
    bilibili = "bilibili"


class Song(BaseModel):
    id: int
    mid: str
    name: str
    desc: str
    singer_mid: str | None = None
    singer_name: str | None = None
    album_mid: str | None = None
    album_name: str | None = None
    time_public: str | None = None
    pic_url: str | None = None


class SearchedSong(BaseModel):
    songs: List[Song]
    num: int


class SongUrls(BaseModel):
    urls: List[str]


class Tag(BaseModel):
    id: int | None = None
    name: str | None = None


class PlayList(BaseModel):
    diss_id: int = 0
    song_num: int = 0
    song_list: List[Song] = []
    desc: str | None = None
    pic_url: str | None = None
    tag: List[Tag] | None = None


class AudioBilibili(BaseModel):
    """
    bilibili音频
    """
    aid: int
    cid: int
    bvid: str
    audio_url: str
    title: str
    part: str
    desc: str
    time_public: str
    owner_id: str
    owner_name: str
    face: str
    pic_url: str


class AudioBilibiliList(BaseModel):
    """
    bilibili音频列表
    """
    list: List[AudioBilibili] = []
    pages: int = 1


class AudioResponse(BaseModel):
    """
    音频响应
    """
    code: int
    msg: str
    data: AudioBilibili | Song | SearchedSong | SongUrls | PlayList | AudioBilibiliList | None = None
