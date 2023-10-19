from random import choice
from platform import system
from subprocess import Popen, PIPE
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE as AsyncPIPE
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    unescape,
    ActionFailed,
)
from nonebot.adapters.onebot.v11.helpers import Cooldown



cmd_help: str = (
    '调用系统命令行\n'
    '⚠危险操作, 谨慎使用!\n\n'
    '>cmd {命令}\n'
    'For example:\n'
    '>cmd echo "Hello World"'
)


shell_help: str = (
    '调用系统命令行\n'
    '(不支持Windows)\n'
    '⚠危险操作, 谨慎使用!\n\n'
    '>shell {命令}\n'
    'For example:\n'
    '>shell echo "Hello World"'
)


_win: tuple = ('windows', 'win32', 'win16')


_flmt_notice: str = choice(['慢...慢一..点❤', '冷静1下', '歇会歇会~~'])


sys_shell = on_command(
    '>shell',
    permission=SUPERUSER,
    priority=1,
    block=True
)

@sys_shell.handle([Cooldown(5, prompt=_flmt_notice)])
async def _(args: Message = CommandArg()):
    for i in _win:
        if system() and (system().lower() in i or i in system().lower()):
            await sys_shell.finish('暂不支持Windows,\n请使用 `>cmd`')
    opt: str = args.extract_plain_text()

    if not opt:
        await sys_shell.finish('发送 >shell.help 以获取帮助')

    if opt == '.help':
        await sys_shell.finish(shell_help)

    content: tuple = await (await create_subprocess_shell(
        unescape(opt),
        stdin=AsyncPIPE,
        stdout=AsyncPIPE,
        stderr=AsyncPIPE
    )).communicate()
    
    if content == (b'', b''):
        msg: str = '\n执行完毕, 没有任何输出呢~'
    elif content[1] == b'':
        msg: str = f'\nstdout:\n{content[0].decode()}\n>执行完毕'
    elif content[0] == b'':
        msg: str = f'\nstderr:\n{content[1].decode()}'
    else :
        msg: str = (f'\nstdout:\n{content[0].decode()}'
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
async def _(args: Message = CommandArg()):
    opt: str = args.extract_plain_text()

    if not opt:
        await sys_cmd.finish('发送 >cmd.help 以获取帮助')

    if opt == '.help':
        await sys_cmd.finish(cmd_help)

    content: tuple = Popen(
        unescape(opt),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        universal_newlines=True
    ).communicate()

    if content == ('',''):
        msg: str = '\n执行完毕, 没有任何输出呢~'
    elif content[1] == '':
        msg: str = f'\nstdout:\n{content[0]}\n>执行完毕'
    elif content[0] == '':
        msg: str = f'\nstderr:\n{content[1]}'
    else :
        msg: str = f'\nstdout:\n{content[0]}\nstderr:\n{content[1]}\n>执行完毕'
    await sys_cmd.finish(msg, at_sender=True)



upload_group_file = on_command(
    '>上传文件',
    permission=SUPERUSER,
    priority=1,
    block=True,
)

@upload_group_file.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    args: list = arg.extract_plain_text().strip().split(maxsplit=1)
    if len(args) < 2:
        await upload_group_file.finish('用法:\n>上传文件 文件名 本地路径')
    filename: str = unescape(args[0])
    filepath: str = unescape(args[1])
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
    args: list = arg.extract_plain_text().strip().split(maxsplit=2)
    if len(args) < 3 or not is_number(args[0]):
        await upload_private_file.finish('用法:\n>私发文件 目标QQ 文件名 本地路径')
    uid: str = args[0]
    filename: str = unescape(args[1])
    filepath: str = unescape(args[2])
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
    e1: str = 'Failed: '
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

