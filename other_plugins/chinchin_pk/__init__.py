import asyncio
from nonebot import on_message
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    GroupMessageEvent,
)

from .src.main import message_processor as chinchin




jjpk = on_message(priority=96, block=False)

@jjpk.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    msg = event.get_plaintext()
    uid = event.user_id
    gid = event.group_id
    uids = [at.data['qq'] for at in event.get_message()['at']]
    at_id = uids[0] if uids else None
    nickname = event.sender.card if event.sender.card else event.sender.nickname
    fuzzy_match = True
    chinchin(bot, matcher, msg, uid, gid, at_id, nickname, fuzzy_match)


