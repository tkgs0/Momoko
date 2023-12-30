from random import choice
from nonebot import on_command, get_driver
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, unescape
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .config import Config
from .data_source import CodeRunner


usage: str = """

使用方法:
    >code {语言}
    {代码}

example:
    >code python
    print('hello world')

发送 >code.list 查看支持的语言

""".strip()


__plugin_meta__ = PluginMetadata(
    name="在线跑代码",
    description="在线跑代码",
    usage=usage,
    type="application"
)


glot_token = Config.parse_obj(get_driver().config.dict()).glot_token

_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])

code_runner = on_command('>code', priority=6, block=True)


@code_runner.handle([Cooldown(5, prompt=_flmt_notice)])
async def _(args: Message = CommandArg()):
    opt = args.extract_plain_text()
    if not opt:
        await code_runner.finish("请发送 >code.help 以获取帮助~！")

    if opt == '.help':
        await code_runner.finish(CodeRunner().help())

    if opt == '.list':
        await code_runner.finish(CodeRunner().list_supp_lang())

    content = str(await CodeRunner().runner(glot_token, unescape(opt)))
    await code_runner.finish(content, at_sender=True)
