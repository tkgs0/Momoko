from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.plugin import on_startswith
from nonebot.permission import SUPERUSER

from .utils import Look

look_like = on_startswith("你看我像", to_me(), priority=5, block=True)

@look_like.handle()
async def _(event: MessageEvent):
    msg = Look.like()
    await look_like.finish(msg)
