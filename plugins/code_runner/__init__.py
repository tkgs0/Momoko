from random import choice
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Message, unescape
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .data_source import CodeRunner


_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])


code_runner = on_command('>code', priority=5, block=True)


@code_runner.handle([Cooldown(5, prompt=_flmt_notice)])
async def _code_runner(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()

    if msg:
        matcher.set_arg("opt", args)
    else:
        content = "请键入 >code.help 以获取帮助~！"
        await code_runner.finish(content)


@code_runner.got("opt", prompt="需要运行的语言及代码？\n获取帮助：>code.help")
async def _(opt: str = ArgPlainText("opt")):

    # 拯救傻瓜用户
    if opt == ">code.help":
        await code_runner.finish(CodeRunner().help())

    content = str(await CodeRunner().runner(unescape(opt)))
    await code_runner.finish(content, at_sender=True)


code_runner_helper = on_command('>code.help', priority=5, block=True)


@code_runner_helper.handle()
async def _():
    await code_runner_helper.finish(CodeRunner().help())


code_supp_list = on_command('>code.list', priority=5, block=True)


@code_supp_list.handle()
async def _():
    await code_supp_list.finish(CodeRunner().list_supp_lang())
