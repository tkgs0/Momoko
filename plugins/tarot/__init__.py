from nonebot.adapters.onebot.v11 import (
    Bot, 
    MessageEvent, 
    GroupMessageEvent,
)
from nonebot.rule import to_me
from nonebot.plugin import on_command, PluginMetadata
from .utils import Tarot


usage: str = """

指令表:
    @Bot 抽塔罗牌

""".strip()


__plugin_meta__ = PluginMetadata(
    name="塔罗牌",
    description="",
    usage=usage,
    type="application"
)


_tarot = on_command("抽塔罗牌", to_me(), priority=5, block=True)

@_tarot.handle()
async def _(bot: Bot, event: MessageEvent):

    gid = event.group_id if isinstance(event, GroupMessageEvent) else 0
    uid = event.user_id
    name = event.sender.card or event.sender.nickname or '老色批'
    
    node = Tarot.get_tarot(uid, name)
    await bot.send_forward_msg(
        user_id=uid if not gid else 0,
        group_id=gid,
        messages=node
    )
