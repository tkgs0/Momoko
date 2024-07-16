from pathlib import Path
import random
import ujson as json
from httpx import AsyncClient
from string import punctuation, whitespace

from nonebot import logger, get_plugin_config
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import Config

config = get_plugin_config(Config)

NICKNAME: str = list(config.nickname)[0]  # bot的nickname
MASTER: str = list(config.superusers)[0]  # bot的主人id
SIZHI_APPID: str = config.sizhi_appid
SIZHI_TIMEOUT: float | None = config.sizhi_timeout
XIAOAI: bool = config.xiaoai_voice

nullpo = MessageSegment.image(file=(Path(__file__).parent / 'resource' / 'nullpo.png'), cache=False)

# 载入骚话
AnimeThesaurus = json.loads(
    (Path(__file__).parent / 'resource' / 'data.json').read_text('utf-8')
)

# hello之类的回复
hello__reply = [
    'ʕ  •ᴥ•ʔ ?',
]


# 从字典里返还消息, 借鉴(抄)的zhenxun-bot
async def get_chat_result(mode: int, text: str, user_id: str) -> str | None | MessageSegment:

    mode_list: list = [xiaosi, xiaoai]
    # 此列表必须与 MODE_LIST 等长

    if len(text) < 10:
        for key in AnimeThesaurus.keys():
            if key in text:
                return random.choice(AnimeThesaurus[key])

    return (await mode_list[mode](text, user_id))


MODE_LIST: list = ['思知', '小爱']
# 此列表必须与 mode_list 等长


# 从思知api拿到消息
async def xiaosi(msg: str, user_id: str) -> str | MessageSegment:

    # 将半角标点和空白符号换成全角空格
    for i in punctuation + whitespace:
        msg = msg.replace(i, '　')

    url = f'https://api.sizhi.com/bot'
    params = {
        'appid': SIZHI_APPID,
        'userid': user_id,
        'spoken': msg
    }
    headers = {
        'referer': 'https://www.sizhi.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers, follow_redirects=True, timeout=SIZHI_TIMEOUT)
            if response.json()['status'] == 0:
                res = response.json()['data']['info']['text']
                for i in ['思知', '小思']:
                    res = res.replace(i, NICKNAME)
                await response.aclose()
                return res
            return 'ʕ  •ᴥ•ʔ……'
        except Exception as e:
            logger.error(repr(e))
            return nullpo


#############
# API已失效 #
#############
# 从小爱api拿到消息
# 语音回复需在 .env 添加 XIAOAI_VOICE=true
async def xiaoai(msg: str, use_id: str) -> str | MessageSegment:

    # 将半角标点和空白符号换成全角空格
    for i in punctuation + whitespace:
        msg = msg.replace(i, '　')

    url = 'http://81.70.100.130/api/xiaoai.php'
    params = {
        'msg': msg,
        'n': 'mp3' if XIAOAI else 'text',
    }
    headers = {
        'referer': 'http://81.70.100.130/xiaochen/xiaoai.php',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers, timeout=15)
            res, status = response.text, response.status_code
            await response.aclose()

            if status == 200:
                content = (
                    await get_voice(res)
                    if XIAOAI
                    else res.replace('小爱', NICKNAME).replace('小米智能助理', '猫')
                )
                return content if content else nullpo
            logger.error(res)

        except Exception as e:
            logger.error(repr(e))
        return nullpo


async def get_voice(url: str) -> MessageSegment | None:

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
                return MessageSegment.record(file=res, cache=False)
            logger.error(res.decode())
        except Exception as e:
            logger.error(repr(e))
