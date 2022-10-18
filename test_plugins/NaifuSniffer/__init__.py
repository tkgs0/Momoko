import asyncio

from nonebot.rule import to_me
from nonebot.plugin import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.helpers import (
    Cooldown,
    CooldownIsolateLevel
)
from .utils import sniff



_fnfs = on_fullmatch("/fnfs", to_me(), priority=5, block=True)

@_fnfs.handle([Cooldown(3600, prompt="慢...慢一..点❤", isolate_level=CooldownIsolateLevel.GLOBAL)])
async def _(bot: Bot):
    await _fnfs.send("Loading......")
    msg = sniff()
    result = await _fnfs.send(msg, at_sender=True)

    loop = asyncio.get_running_loop()
    loop.call_later(
        90,  # 消息撤回等待时间 单位秒
        lambda: asyncio.ensure_future(bot.delete_msg(message_id=result["message_id"])),
    )
