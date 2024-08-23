import yaml
from pydantic import BaseModel, ConfigDict
from typing import Dict, Tuple
from httpx import AsyncClient
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from nonebot import on_command, get_plugin_config
from nonebot.config import Config as nonebotConfig
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .config import Config


class Model(BaseModel):
    model_config = ConfigDict(extra="ignore")
    params: Dict | None = None
    headers: Dict | None = None
    cookies: Dict | None = None
    timeout: float | None = 60.0


cmd: str = get_plugin_config(Config).call_http_call
cmd_start: str = min(list(get_plugin_config(nonebotConfig).command_start))

usage= f'''

{cmd_start}{cmd} url
params:
  xxx: xxx

example:
  {cmd_start}{cmd} http://127.0.0.1:8080/send_msg
  params:
    token: XXX
    user_id: 123456
    group_id: 123456
    message: XXXXXX
  headers:
    user-agent: xxx
  cookies:
    session: xxx
  timeout: 60.0

ⓘ仅支持http(s)

'''.strip()


__plugin_meta__ = PluginMetadata(
    name="call_http",
    description="call call 你的API🥵",
    usage=usage,
    type="application"
)


callapi = on_command(
    cmd,
    permission=SUPERUSER,
    priority=1,
    block=True
)

@callapi.handle()
async def _(args: Message = CommandArg()):
    if not args:
        await callapi.finish(usage)
    content = args.extract_plain_text().split(maxsplit=1)
    url = content[0]
    arg = content[1] if len(content) > 1 else "params:"
    try:
        params, headers, cookies, timeout = handle_params(arg)
        res = await get_api(url, params, headers, cookies, timeout)
    except Exception as e:
        res = repr(e)
    await callapi.finish(Message(res))


def handle_params(msg: str) -> Tuple:
    conf = yaml.safe_load(msg)
    config = Model.model_validate(conf)
    return config.params, config.headers, config.cookies, config.timeout


async def get_api(
    url: str,
    params: dict,
    headers: dict,
    cookies: dict,
    timeout: float | None
) -> str | MessageSegment:
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers, cookies=cookies, follow_redirects=True, timeout=timeout)

            if "application/json" == response.headers.get("Content-Type"):
                res = json.dumps(response.json(), indent=2, ensure_ascii=False)
            elif "audio" in response.headers.get("Content-Type"):
                res = MessageSegment.record(response.content, cache=False)
            elif "video" in response.headers.get("Content-Type"):
                res = MessageSegment.video(response.content, cache=False)
            elif "image" in response.headers.get("Content-Type"):
                res = MessageSegment.image(response.content, cache=False)
            else:
                res = response.content.decode()
            await response.aclose()
            return res
        except Exception as e:
            return repr(e)

