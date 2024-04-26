# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/26 : 14:06
from pydantic import BaseModel

from models.music import AudioResponse


def get_audio_response(code: int, msg: str, data: BaseModel = None) -> AudioResponse:
    """
    :param code: 状态码
    :param msg: 状态信息
    :param data: 数据
    :return:
    """
    return AudioResponse(**{
        "code": code,
        "msg": msg,
        "data": data
    })
