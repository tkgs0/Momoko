from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    unescape
)
from nonebot.params import CommandArg
from nonebot.plugin import on_command
from nonebot.permission import SUPERUSER
import httpx



_help = """
⛦ 🍑 Momoko 开源 Project ⛥
* OneBot + NoneBot + Python
* Copyright © 2021 - 2023 tkgs0. All Rights Reserved.
* 项目地址: https://github.com/tkgs0/Momoko
* 使用帮助: https://github.com/tkgs0/Momoko#功能表
""".strip()

help = on_command(
    "help",
    rule=to_me(),
    aliases={"帮助","menu","菜单"},
    priority=5, block=True
)

@help.handle()
async def _():
    await help.finish(_help)



echo = on_command(
    "：",
    aliases={":", "曰"},
    rule=to_me(),
    priority=5,
    block=True,
    permission=SUPERUSER
)

@echo.handle()
async def echo_escape(arg: Message = CommandArg()):
    msg = unescape(str(arg))
    await echo.finish(Message(msg))



_snapshot = on_command(
    "/快照",
    priority=5,
    block=True,
    permission=SUPERUSER
)

@_snapshot.handle()
async def _(arg: Message = CommandArg()):
    url = arg.extract_plain_text()
    url = f"https://image.thum.io/get/width/1280/crop/1440/viewportWidth/1280/png/noanimate/{url}"
    try:
        res = httpx.get(url, headers=headers, timeout=30) 
        await _snapshot.send(MessageSegment.image(file=res.content))
        res.close()
    except Exception as e:
        await _snapshot.finish(repr(e))


headers = {
    'Referer': 'https://github.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
