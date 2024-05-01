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
from nonebot.adapters.onebot.v11 import Message


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    params: Dict = {}
    headers: Dict = {}
    cookies: Dict = {}


usage='''

/api url
param=XXX

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
) -> str:
    if not url.startswith('http://') or url.startswith('https://'):
        url = 'http://' + url

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers, cookies=cookies, follow_redirects=True, timeout=60)
            try:
                res: str = json.dumps(response.json(), indent=2, ensure_ascii=False)
            except:
                res: str = response.text
            await response.aclose()
            return res
        except Exception as e:
            return repr(e)

