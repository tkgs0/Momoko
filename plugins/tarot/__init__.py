from nonebot.adapters.onebot.v11 import (
    Bot, 
    MessageEvent, 
    PrivateMessageEvent, 
    GroupMessageEvent, 
)
from nonebot.rule import to_me
from nonebot.plugin import on_command
from .utils import Tarot

_tarot = on_command("抽塔罗牌", to_me(), priority=5, block=True)

@_tarot.handle()
async def _(bot: Bot, event: MessageEvent):
    node = Tarot.get_tarot()
    await bot.send_forward_msg(
        user_id=event.user_id if isinstance(event, PrivateMessageEvent) else 0,
        group_id=event.group_id if isinstance(event, GroupMessageEvent) else 0,
        messages=node,
    )
