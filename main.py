# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/17 : 17:59

from fastapi import FastAPI
import uvicorn

from models.music import SourceName, Song
from routers import qq_music_router, bilibili_router

app = FastAPI()

app.include_router(qq_music_router.router)
app.include_router(bilibili_router.router)


@app.get("/")
def root():
    """
    Root URL
    :return:
    """
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=51111)
