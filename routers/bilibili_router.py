# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/26 : 13:45

from fastapi import APIRouter, Response

from models.music import AudioResponse, AudioBilibiliList
from api.bilibili import BilibiliClient
from routers.tools import get_audio_response

router = APIRouter(
    prefix="/bilibili",
    tags=["Bilibili Audio"]
)

client = BilibiliClient()


@router.get("/audio", response_model=AudioResponse)
async def audio(bvid: str):
    bilibili_audio_list: AudioBilibiliList | None = await client.get_audio(bvid)
    if bilibili_audio_list is not None:
        return get_audio_response(code=0, msg='成功!', data=bilibili_audio_list)
    else:
        return get_audio_response(code=-1, msg='失败!', data=bilibili_audio_list)
