from pathlib import Path
import random
import nonebot
from nonebot.log import logger
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from httpx import AsyncClient


Bot_NICKNAME: str = list(nonebot.get_driver().config.nickname)[0]      # bot的nickname,可以换成你自己的
Bot_MASTER: str = list(nonebot.get_driver().config.superusers)[0]      # bot的主人名称,也可以换成你自己的

# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(__file__).parent / 'resource' / 'data.json', 'r', encoding='utf8'))

# hello之类的回复
hello__reply = [
    'ʕ  •ᴥ•ʔ ?',
]


# 从字典里返还消息, 借鉴(抄)的zhenxun-bot
async def get_chat_result(text: str):
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key])


headers = {
    'referer': 'https://www.ownthink.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}


# 从ownthink_api拿到消息
async def get_reply(msg):

    url = f'https://api.ownthink.com/bot'
    params = {
        'appid': 'xiaosi',
        'userid': 'user',
        'spoken': msg,
    }

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers)
            if response.json()['data']['type'] == 5000:
                res = response.json()['data']['info']['text'].replace('小思', Bot_NICKNAME)
                return res
            else:
                return 'ʕ  •ᴥ•ʔ……'
        except Exception as e:
            logger.warning(repr(e))
            return 'ʕ  •ᴥ•ʔ</>'

