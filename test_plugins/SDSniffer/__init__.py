from pathlib import Path
from random import choice
from subprocess import Popen, PIPE

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.helpers import (
    Cooldown,
    CooldownIsolateLevel
)

import asyncio


_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])
file_path = Path(__file__).parent / "fsds.py"

_fsds = on_command('>fsds', priority=5, block=True)

@_fsds.handle([Cooldown(
    180,
    prompt=_flmt_notice,
    isolate_level=CooldownIsolateLevel.GLOBAL
)])
async def _(bot: Bot):
    await _fsds.send("Loading......")

    opt = "python " + str(file_path)
    content = Popen(
        opt,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        universal_newlines=True
    ).communicate()

    msg = f"\n{content[0]}"
    result = await _fsds.send(msg, at_sender=True)
    
    loop = asyncio.get_running_loop()
    loop.call_later(
        90,  # 消息撤回等待时间 单位秒
        lambda: asyncio.ensure_future(
            bot.delete_msg(message_id=result["message_id"])
        ),
    )

