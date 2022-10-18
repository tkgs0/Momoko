import asyncio, time

from nonebot.rule import to_me
from nonebot.plugin import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.helpers import Cooldown
from .utils import run



_fsds = on_fullmatch("fsds", to_me(), priority=5, block=True)

@_fsds.handle([Cooldown(1800, prompt="慢...慢一..点❤")])
async def _(bot: Bot):
    await _fsds.send("Loading......")
    st = time.time()
    try:
        msg = await run()
    except Exception as e:
        msg = "\n"+str(repr(e))
    msg += f"\nCosts: {time.time()-st:.2f}s"
    print("\033[1;35mComplete\033[0m")
    result = await _fsds.send(msg, at_sender=True)

    loop = asyncio.get_running_loop()
    loop.call_later(
        90,  # 消息撤回等待时间 单位秒
        lambda: asyncio.ensure_future(bot.delete_msg(message_id=result["message_id"])),
    )
