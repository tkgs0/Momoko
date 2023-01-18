from nonebot.rule import to_me
from nonebot.plugin import on_startswith

from .utils import Look

look_like = on_startswith("你看我像", to_me(), priority=5, block=True)

@look_like.handle()
async def _():
    msg = Look.like()
    await look_like.finish(msg)
