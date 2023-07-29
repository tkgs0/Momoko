from random import random
from nonebot import on_regex
from nonebot.internal.adapter import Event


six = on_regex(r"^6+$", priority=5, block=False)


@six.handle()
async def _(event: Event):
    if random()*10//1 == 6.0:
        await six.finish(event.get_message())
