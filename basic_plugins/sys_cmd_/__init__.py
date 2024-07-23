from platform import system
from subprocess import Popen, PIPE
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE as AsyncPIPE
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.internal.adapter import Message

from .utils import unescape


usage: str = '''
发送 /sh 或 /cmd 查看帮助.

如果 COMMAND_START=["/"]
那么 `/sh` `/cmd` 应该写作 `//sh` `//cmd`
'''.strip()


__plugin_meta__ = PluginMetadata(
    name="命令行",
    description="操作Bot所在系统的命令行",
    usage=usage,
    type="application",
    homepage="https://github.com/tkgs0/nonebot-plugin-system-command"
)


cmd_help: str = '''
调用系统命令行
⚠危险操作, 谨慎使用!

/cmd {命令}
For example:
/cmd echo "Hello World"

如果 COMMAND_START=["/"]
那么 /cmd 应该写作 //cmd
'''.strip()


shell_help: str = '''
调用系统命令行
(不支持Windows)
⚠危险操作, 谨慎使用!

/sh {命令}
For example:
/sh echo "Hello World"

如果 COMMAND_START=["/"]
那么 /sh 应该写作 //sh
'''.strip()


_win: tuple = ('windows', 'win32', 'win16')


sys_shell = on_command(
    '/sh',
    permission=SUPERUSER,
    priority=1,
    block=True
)

@sys_shell.handle()
async def _(args: Message = CommandArg()):
    for i in _win:
        if system() and (system().lower() in i or i in system().lower()):
            await sys_shell.finish('暂不支持Windows,\n请尝试使用 `/cmd`')
    opt: str = args.extract_plain_text()

    if not opt:
        await sys_shell.finish(shell_help)

    content: tuple = await (await create_subprocess_shell(
        unescape(opt),
        stdin=AsyncPIPE,
        stdout=AsyncPIPE,
        stderr=AsyncPIPE
    )).communicate()
    
    if content == (b'', b''):
        msg: str = '没有任何输出呢~'
    elif content[1] == b'':
        msg: str = f'stdout:\n{content[0].decode()}'
    elif content[0] == b'':
        msg: str = f'stderr:\n{content[1].decode()}'
    else :
        msg: str = (f'stdout:\n{content[0].decode()}'
               f'\nstderr:\n{content[1].decode()}')
    await sys_shell.finish(
        '执行完毕;\n' + (
            msg
            if len(msg) <= 4500
            else msg[:4400] + '\n......\n......\n......\n(太多了发不出...)'
        ),
        at_sender=True
    )


sys_cmd = on_command(
    '/cmd',
    priority=1,
    block=True,
    permission=SUPERUSER
)


@sys_cmd.handle()
async def _(args: Message = CommandArg()):
    opt: str = args.extract_plain_text()

    if not opt:
        await sys_cmd.finish(cmd_help)

    content: tuple = Popen(
        unescape(opt),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        universal_newlines=True
    ).communicate()

    if content == ('', ''):
        msg: str = '没有任何输出呢~'
    elif content[1] == '':
        msg: str = f'stdout:\n{content[0]}'
    elif content[0] == '':
        msg: str = f'stderr:\n{content[1]}'
    else :
        msg: str = f'stdout:\n{content[0]}\nstderr:\n{content[1]}'
    await sys_cmd.finish(
        '执行完毕;\n' + (
            msg
            if len(msg) <= 4500
            else msg[:4400] + '\n......\n......\n......\n(太多了发不出...)'
        ),
        at_sender=True
    )
