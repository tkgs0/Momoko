from pathlib import Path
import random
import ujson as json
from httpx import AsyncClient
from urllib.parse import quote

from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import Config

config = Config.parse_obj(get_driver().config.dict())

Bot_NICKNAME: str = list(config.nickname)[0]  # bot的nickname
Bot_MASTER: str = list(config.superusers)[0]  # bot的主人id
xiaoai_key: str = config.apibug_xiaoai

# 载入词库(这个词库有点涩)
AnimeThesaurus = json.loads(
    (Path(__file__).parent / 'resource' / 'data.json').read_text('utf-8')
)

# hello之类的回复
hello__reply = [
    'ʕ  •ᴥ•ʔ ?',
]


# 从字典里返还消息, 借鉴(抄)的zhenxun-bot
async def get_chat_result(text: str) -> str | None:
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key])


# 从思知api拿到消息
async def xiaosi(msg) -> tuple:

    url = f'https://api.ownthink.com/bot'
    params = {
        'appid': 'xiaosi',
        'userid': 'user',
        'spoken': quote(msg),
    }
    headers = {
        'referer': 'https://www.ownthink.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers)
            if response.json()['data']['type'] == 5000:
                res = response.json()['data']['info']['text'].replace('小思', Bot_NICKNAME)
                await response.aclose()
                return res, None
            else:
                return 'ʕ  •ᴥ•ʔ……', None
        except Exception as e:
            logger.error(repr(e))
            return 'ʕ  •ᴥ•ʔ</>', None


# 从小爱api拿到消息
async def xiaoai(msg) -> tuple:
    if not xiaoai_key:
        return '未配置小爱apikey, 请联系bot管理员', None

    url = 'https://apibug.cn/api/xiaoai/'
    params = {
        'apiKey': xiaoai_key,
        'msg': quote(msg),
    }
    headers = {
        'referer': 'https://apibug.cn/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers)
            res = response.json()
            await response.aclose()
            
            text = res['text']
            voice = await get_voice(res['mp3'])
            
            return text, MessageSegment.record(file=voice, cache=False) if voice else None

        except Exception as e:
            logger.error(repr(e))
            return 'ʕ  •ᴥ•ʔ</>', None


async def get_voice(url: str) -> bytes | None:

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'content-type': 'audio/mpeg',
    }
    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, headers=headers, timeout=60)
            res, status = response.content, response.status_code
            await response.aclose()
            if status == 200:
                return res
            else:
                logger.error(res.decode())
        except Exception as e:
            logger.error(repr(e))
