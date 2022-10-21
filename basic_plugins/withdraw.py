from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
import re

withdraw_msg = on_fullmatch("撤回", priority=5, block=True, permission=SUPERUSER)

@withdraw_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    r = re.search(r"\[CQ:reply,id=(-?\d*)]", event.raw_message)
    if r:
        await bot.delete_msg(message_id=int(r.group(1)))

