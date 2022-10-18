import asyncio, time

from nonebot.rule import to_me
from nonebot.plugin import on_fullmatch
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent
)
from nonebot.adapters.onebot.v11.helpers import (
    Cooldown,
    CooldownIsolateLevel
)
from .utils import run



_fnfs = on_fullmatch("fnfs", to_me(), priority=5, block=True)
_fnfs_ = on_fullmatch("/fnfs", priority=5, block=True, permission=SUPERUSER)

@_fnfs_.handle()
@_fnfs.handle([Cooldown(1800, prompt="慢...慢一..点❤", isolate_level=CooldownIsolateLevel.GLOBAL)])
async def _(bot: Bot, event: MessageEvent):
    await _fnfs.send("Loading......")
    st = time.time()
    try:
        msg = await run()
    except Exception as e:
        msg = "\n"+str(repr(e))
    msg += f"\nCosts: {time.time()-st:.2f}s"
    print("\n\033[1;35mComplete\033[0m")
    result = await _fnfs.send(msg, at_sender=True)

    loop = asyncio.get_running_loop()
    loop.call_later(
        90,  # 消息撤回等待时间 单位秒
        lambda: asyncio.ensure_future(bot.delete_msg(message_id=result["message_id"])),
    )
    await _fnfs.finish("complete")