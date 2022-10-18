from random import choice, randint
from nonebot.plugin import on_command
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, Message
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .data_source import Funny



_fake_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])


fake_msg = on_command("/fakemsg", priority=5, block=True, permission=SUPERUSER)


@fake_msg.handle([Cooldown(60, prompt=_fake_flmt_notice)])
async def _ready_fake(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("content", args)


@fake_msg.got("content", "内容呢？格式：qq-name-content\n可构造多条，以上仅为一条，使用换行隔开")
async def _deal_fake(
    bot: Bot, event: GroupMessageEvent, content: str = ArgPlainText("content")
):
    group_id = event.group_id
    
    try:
        node = Funny().fake_msg(content)
    except Exception:
        await fake_msg.finish("内容格式错误，请检查")

    try:
        await bot.send_group_forward_msg(group_id=group_id, messages=node)
    except Exception:
        await fake_msg.finish("构造失败惹...可能寄了...")
