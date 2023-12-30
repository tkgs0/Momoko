import re
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


usage='''

/api url
param=XXX

example:
  /api http://127.0.0.1:8080/send_msg
  token=XXX
  user_id=123456
  group_id=123456
  message=XXXXXX

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
    url, params = args.extract_plain_text().split(maxsplit=1)
    try:
        res = await get_api(url, handle_params(params))
    except Exception as e:
        res = repr(e)
    await callapi.finish(res)


def handle_params(msg: str) -> dict:
    args: list = msg.split('\n')
    params: dict = {}
    for i in args:
        par = i.split('=', maxsplit=1)
        params.update({par[0]: par[1]})
    return params


async def get_api(url: str, params: dict) -> str:
    if not url.startswith('http://') or url.startswith('https://'):
        url = 'http://' + url

    headers: dict = {
        'referer': re.search(r'^http(s?):\/\/[^\/]*', url).group(),  # type: ignore
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers, follow_redirects=True, timeout=60)
            try:
                res: str = json.dumps(response.json(), indent=2, ensure_ascii=False)
            except:
                res: str = response.text
            await response.aclose()
            return res
        except Exception as e:
            return repr(e)

