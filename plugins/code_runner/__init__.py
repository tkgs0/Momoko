from random import choice
from nonebot import on_command, get_driver
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, unescape
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .config import Config
from .data_source import CodeRunner


glot_token = Config.parse_obj(get_driver().config.dict()).glot_token

_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])

code_runner = on_command('>code', priority=6, block=True)


@code_runner.handle([Cooldown(5, prompt=_flmt_notice)])
async def _(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.state["opt"] = args


@code_runner.got("opt", prompt="需要运行的语言及代码？\n获取帮助：>code.help")
async def _(matcher: Matcher):
    opt = matcher.state["opt"].extract_plain_text()

                        # 拯救傻瓜用户
    if opt in ('.help', '>code.help'):
        await code_runner.finish(CodeRunner().help())

    if opt == '.list':
        await code_runner.finish(CodeRunner().list_supp_lang())

    content = str(await CodeRunner().runner(glot_token, unescape(opt)))
    await code_runner.finish(content, at_sender=True)
