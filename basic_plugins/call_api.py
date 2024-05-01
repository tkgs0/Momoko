import yaml
from pydantic import BaseModel, ConfigDict
from typing import Dict, Tuple
from httpx import AsyncClient
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, MessageSegment


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    params: Dict = {}
    headers: Dict = {}
    cookies: Dict = {}


usage='''

/api url
params:
  xxx: xxx

example:
  /api http://127.0.0.1:8080/send_msg
  params:
    token: XXX
    user_id: 123456
    group_id: 123456
    message: XXXXXX
  headers:
    user-agent: xxx
  cookies:
    session: xxx

ⓘ暂不支持ws/wss

'''.strip()


__plugin_meta__ = PluginMetadata(
    name="call_api",
    description="call call 你的API🥵",
    usage=usage,
    type="application"
)


callapi = on_command(
    '/api',
    permission=SUPERUSER,
    priority=1,
    block=True
)

@callapi.handle()
async def _(args: Message = CommandArg()):
    if not args:
        await callapi.finish(usage)
    url, arg = args.extract_plain_text().split(maxsplit=1)
    try:
        params, headers, cookies = handle_params(arg)
        res = await get_api(url, params, headers, cookies)
    except Exception as e:
        res = repr(e)
    await callapi.finish(Message(res))


def handle_params(msg: str) ->Tuple:
    conf = yaml.safe_load(msg)
    config = Config.model_validate(conf)
    return config.params, config.headers, config.cookies


async def get_api(
    url: str,
    params: dict,
    headers: dict,
    cookies: dict
) -> str | MessageSegment:
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers, cookies=cookies, follow_redirects=True, timeout=60)

            if "application/json" == response.headers.get("Content-Type"):
                res = json.dumps(response.json(), indent=2, ensure_ascii=False)
            elif "audio" in response.headers.get("Content-Type"):
                res = MessageSegment.record(response.content)
            elif "video" in response.headers.get("Content-Type"):
                res = MessageSegment.video(response.content)
            elif "image" in response.headers.get("Content-Type"):
                res = MessageSegment.image(response.content)
            else:
                res = response.content.decode()
            await response.aclose()
            return res
        except Exception as e:
            return repr(e)

