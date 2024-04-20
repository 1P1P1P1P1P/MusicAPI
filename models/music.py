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
