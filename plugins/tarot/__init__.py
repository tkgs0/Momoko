from nonebot.adapters.onebot.v11 import (
    Bot, 
    MessageEvent, 
)
from nonebot.rule import to_me
from nonebot.plugin import on_command
from .utils import Tarot

_tarot = on_command("抽塔罗牌", to_me(), priority=5, block=True)

@_tarot.handle()
async def _(bot: Bot, event: MessageEvent):

    gid = vars(event).get('group_id', 0)
    uid = event.user_id
    name = str(event.sender.nickname)
    
    node = Tarot.get_tarot(uid, name)
    await bot.send_forward_msg(
        user_id=uid if not gid else 0,
        group_id=gid,
        messages=node
    )
