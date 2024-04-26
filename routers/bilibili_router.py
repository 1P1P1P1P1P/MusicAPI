# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/26 : 13:45

from fastapi import APIRouter, Response

from models.music import AudioResponse
from api.bilibili import BilibiliClient
from routers.tools import get_audio_response

router = APIRouter(
    prefix="/bilibili",
    tags=["Bilibili Audio"]
)

client = BilibiliClient()


@router.get("/audio", response_model=AudioResponse)
def song_search(bvid: str):
    bilibili_audio = client.get_audio_url(bvid)
    if bilibili_audio is not None:
        return get_audio_response(code=0, msg='成功!', data=bilibili_audio)
    else:
        return get_audio_response(code=-1, msg='失败!', data=bilibili_audio)
