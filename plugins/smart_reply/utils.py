from pathlib import Path
import os
import random
import nonebot
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from httpx import AsyncClient
import re

Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]      # bot的nickname,可以换成你自己的
Bot_MASTER: str = list(nonebot.get_driver().config.superusers)[0]      # bot的主人名称,也可以换成你自己的

# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "resource")) / "data.json", "r", encoding="utf8"))

# hello之类的回复
hello__reply = [
    f"{Bot_NICKNAME}不在呢。",
]

# 从字典里返还消息, 抄(借鉴)的zhenxun-bot
async def get_chat_result(text: str):
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key])

# 从ownthink_api拿到消息
async def get_reply(url):
    async with AsyncClient() as client:
        response = await client.get(url)
        if response.json()["data"]["type"] == 5000:
            res = response.json()["data"]["info"]["text"].replace("小思", Bot_NICKNAME)
            res = re.sub(u"\\{.*?\\}", "", res)
            return res
        else:
            pass
        
        

