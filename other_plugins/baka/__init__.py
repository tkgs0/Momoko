import random, asyncio
from nonebot import on_message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
)


baka = on_message(priority=98, block=False)

@baka.handle()
async def _(event: MessageEvent, matcher: Matcher):
    msg = event.get_plaintext()
    if len(msg) > 250:
        matcher.stop_propagation()
        await asyncio.sleep(random.random()*2+1)
        await baka.send('阿巴阿巴')
        await baka.finish('字太多不看')
