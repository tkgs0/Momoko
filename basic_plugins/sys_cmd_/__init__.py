from platform import system
from subprocess import Popen, PIPE
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE as AsyncPIPE
from random import choice
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    unescape,
    ActionFailed,
)
from nonebot.adapters.onebot.v11.helpers import Cooldown



cmd_help = (
    '调用系统命令行\n'
    '⚠危险操作, 谨慎使用!\n\n'
    '>cmd {命令}\n'
    'For example:\n'
    '>cmd echo "Hello World"'
)


shell_help = (
    '调用系统命令行\n'
    '(不支持Windows)\n'
    '⚠危险操作, 谨慎使用!\n\n'
    '>shell {命令}\n'
    'For example:\n'
    '>shell echo "Hello World"'
)


_win = ('windows', 'Windows', 'win32', 'Win32', 'win16', 'Win16')


_flmt_notice = choice(['慢...慢一..点❤', '冷静1下', '歇会歇会~~'])


sys_shell = on_command(
    '>shell',
    permission=SUPERUSER,
    priority=1,
    block=True
)

@sys_shell.handle([Cooldown(5, prompt=_flmt_notice)])
async def _(matcher: Matcher, args: Message = CommandArg()):
    for i in _win:
        if system() and (system() in i or i in system()):
            await sys_shell.finish('暂不支持Windows,\n请使用同步方法 `>cmd`')
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg('opt', args)


@sys_shell.got('opt', prompt='请输入命令内容\n获取帮助：>shell.help')
async def _(opt: str = ArgPlainText('opt')):

    # 拯救傻瓜用户
    if opt.startswith('>shell.help'):
        await sys_shell.finish(shell_help)

    content = await (await create_subprocess_shell(
        unescape(opt),
        stdin=AsyncPIPE,
        stdout=AsyncPIPE,
        stderr=AsyncPIPE
    )).communicate()
    
    if content == (b'', b''):
        msg = '\n执行完毕, 没有任何输出呢~'
    elif content[1] == b'':
        msg = f'\nstdout:\n{content[0].decode()}\n>执行完毕'
    elif content[0] == b'':
        msg = f'\nstderr:\n{content[1].decode()}'
    else :
        msg = (f'\nstdout:\n{content[0].decode()}'
               f'\nstderr:\n{content[1].decode()}'
               '\n>执行完毕')
    await sys_shell.finish(msg, at_sender=True)


sys_cmd = on_command(
    '>cmd',
    priority=1,
    block=True,
    permission=SUPERUSER
)


@sys_cmd.handle([Cooldown(5, prompt=_flmt_notice)])
async def _(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg('opt', args)


@sys_cmd.got('opt', prompt='请输入命令内容\n获取帮助：>cmd.help')
async def _(opt: str = ArgPlainText('opt')):

    # 拯救傻瓜用户
    if opt.startswith('>cmd.help'):
        await sys_cmd.finish(cmd_help)

    content = Popen(
        unescape(opt),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        universal_newlines=True
    ).communicate()

    if content == ('',''):
        msg = '\n执行完毕, 没有任何输出呢~'
    elif content[1] == '':
        msg = f'\nstdout:\n{content[0]}\n>执行完毕'
    elif content[0] == '':
        msg = f'\nstderr:\n{content[1]}'
    else :
        msg = f'\nstdout:\n{content[0]}\nstderr:\n{content[1]}\n>执行完毕'
    await sys_cmd.finish(msg, at_sender=True)


sys_cmd_helper = on_command('>cmd.help', priority=5, block=True)

@sys_cmd_helper.handle()
async def _():
    await sys_cmd_helper.finish(cmd_help)




upload_group_file = on_command(
    '>上传文件',
    permission=SUPERUSER,
    priority=1,
    block=True,
)

@upload_group_file.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split(maxsplit=1)
    if len(args) < 2:
        await upload_group_file.finish('用法:\n>上传文件 文件名 本地路径')
    filename = unescape(args[0])
    filepath = unescape(args[1])
    try:
        await bot.upload_group_file(
            group_id=event.group_id,
            name=filename,
            file=filepath
        )
    except ActionFailed as e:
        await upload_group_file.finish(err_info(e))
    await upload_group_file.finish()


upload_private_file = on_command(
    '>私发文件',
    permission=SUPERUSER,
    priority=1,
    block=True,
)

@upload_private_file.handle()
async def _(bot: Bot, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split(maxsplit=2)
    if len(args) < 3 or not is_number(args[0]):
        await upload_private_file.finish('用法:\n>私发文件 目标QQ 文件名 本地路径')
    uid = args[0]
    filename = unescape(args[1])
    filepath = unescape(args[2])
    try:
        await bot.upload_private_file(
            user_id=int(uid),
            name=filename,
            file=filepath
        )
    except ActionFailed as e:
        await upload_private_file.finish(err_info(e))
    await upload_private_file.finish()


def err_info(e: ActionFailed) -> str:
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

