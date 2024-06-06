from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Message,
    unescape
)
from nonebot.params import CommandArg
from nonebot.plugin import on_command, PluginMetadata
from nonebot.permission import SUPERUSER


usage: str = """

@机器人 并加上 冒号 ： 发送你想让机器人说的话

示例:
    @桃桃酱 ：xxxxx

""".strip()


__plugin_meta__ = PluginMetadata(
    name="echo",
    description="啊吧啊吧",
    usage=usage,
    type="application"
)


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
