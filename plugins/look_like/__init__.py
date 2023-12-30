from nonebot.rule import to_me
from nonebot.plugin import on_startswith, PluginMetadata

from .utils import Look


usage: str = """

指令表:
    @Bot 你看我像

""".strip()


__plugin_meta__ = PluginMetadata(
    name="look_like",
    description="你看我像人吗?",
    usage=usage,
    type="application"
)


look_like = on_startswith("你看我像", to_me(), priority=5, block=True)

@look_like.handle()
async def _():
    msg = Look.like()
    await look_like.finish(msg)
