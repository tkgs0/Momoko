from nonebot import on_message, on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
)

from .src.main import KEYWORDS, message_processor as chinchin


_help = [
    '/牛子',
    '/pk @用户',
    '/🔒(/suo/嗦/锁)我',
    '/🔒(/suo/嗦/锁) @用户',
    '/打胶',
    '/看他牛子(/看看牛子) @用户',
    '/注册牛子',
    '/牛子排名(/牛子排行)',
]


jjpk = on_message(priority=96, block=False)

@jjpk.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    msg = event.get_plaintext()
    if msg.startswith('/'):
        msg = msg.replace('/', '', 1)
        x = 0
        for i in KEYWORDS.values():
            for j in i:
                if j in msg:
                    x = 1
        if not x:
            return
        uid = event.user_id
        gid = event.group_id
        uids = [at.data['qq'] for at in event.get_message()['at']]
        at_id = uids[0] if uids else None
        nickname = event.sender.card if event.sender.card else event.sender.nickname
        fuzzy_match = True
        chinchin(bot, matcher, msg, uid, gid, at_id, nickname, fuzzy_match)


jjpk_help = on_command(
    '牛子帮助',
    priority=5,
    block=True
)

@jjpk_help.handle()
async def _(event: GroupMessageEvent):
    event.user_id
    await jjpk_help.finish('\n'.join(_help))
