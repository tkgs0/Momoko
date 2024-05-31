from nonebot import on_command, logger
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .Gua64 import encode, decode

usage: str = """

指令表:
    64卦加密 xxx
    64卦解密 xxx

""".strip()


__plugin_meta__ = PluginMetadata(
    name="64卦加密",
    description="将文本转换成卦象",
    usage=usage,
    type="application"
)


en64Gua = on_command(
    "64卦加密",
    aliases={"六十四卦加密"},
    priority=5,
    block=True
)

@en64Gua.handle()
async def _(args: Message = CommandArg()):
    arg: str = args.extract_plain_text()
    msg: str = encode(arg.encode()).decode() if arg else "需要内容"
    await en64Gua.finish(msg)


de64Gua = on_command(
    "64卦解密",
    aliases={"六十四卦解密"},
    priority=5,
    block=True
)


@de64Gua.handle()
async def _(args: Message = CommandArg()):
    arg: str = args.extract_plain_text()
    try:
        msg: str = decode(arg.encode()).decode() if arg else "需要内容"
    except KeyError as e:
        logger.error(repr(e))
        msg: str = "格式错误: 不是有效的卦象文本"
    except UnicodeDecodeError as e:
        logger.error(repr(e))
        msg: str = "解码失败: 无法转换成有效的utf-8字符串文本"
    await de64Gua.finish(msg)
