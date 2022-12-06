from subprocess import Popen, PIPE
from random import choice
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import (
    Message,
    unescape
)
from nonebot.adapters.onebot.v11.helpers import Cooldown



def help() -> str:
    return (
        "调用系统命令行\n"
        "⚠危险操作, 谨慎使用!\n\n"
        ">cmd {命令}\n"
        "For example:\n"
        ">cmd echo \"Hello World\""
    )


_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])


sys_cmd = on_command('>cmd', priority=6, block=True, permission=SUPERUSER)


@sys_cmd.handle([Cooldown(5, prompt=_flmt_notice)])
async def _sys_cmd(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("opt", args)


@sys_cmd.got("opt", prompt="请输入命令内容\n获取帮助：>cmd.help")
async def _(opt: str = ArgPlainText("opt")):

    # 拯救傻瓜用户
    if opt.startswith(">cmd.help"):
        await sys_cmd.finish(help())

    content = Popen(
        unescape(opt),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        universal_newlines=True
    ).communicate()

    msg = None
    if content == ('',''):
        msg = "\n执行完毕, 没有任何输出呢~"
    elif content[1] == '':
        msg = f"\nstdout:\n{content[0]}\n>执行完毕"
    elif content[0] == '':
        msg = f"\nstderr:\n{content[1]}"
    else :
        msg = f"\nstdout:\n{content[0]}\nstderr:\n{content[1]}\n>执行完毕"
    await sys_cmd.finish(msg, at_sender=True)


sys_cmd_helper = on_command('>cmd.help', priority=5, block=True)

@sys_cmd_helper.handle()
async def _():
    await sys_cmd_helper.finish(help())
