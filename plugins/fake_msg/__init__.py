from random import choice
from nonebot.plugin import on_command, PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message
)
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .data_source import Funny


usage: str = """

使用方法:
    /fakemsg
    qq号-昵称-消息内容

example:
    /fakemsg
    123456789-桃桃酱-不可以色色
    987654321-路人甲-我就要色色

""".strip()


__plugin_meta__ = PluginMetadata(
    name="合并转发",
    description="赝作合并转发消息",
    usage=usage,
    type="application"
)


_fake_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])


fake_msg = on_command("/fakemsg", priority=5, block=True, permission=SUPERUSER)


@fake_msg.handle([Cooldown(15, prompt=_fake_flmt_notice)])
async def _(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("content", args)


@fake_msg.got("content", "内容呢？格式：qq-name-content\n可构造多条，以上仅为一条，使用换行隔开")
async def _(
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
