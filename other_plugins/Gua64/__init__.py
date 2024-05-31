from nonebot import on_command, logger
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    MessageEvent,
    GroupMessageEvent,
    ActionFailed
)

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
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    arg: str = args.extract_plain_text()
    if not arg:
        await de64Gua.finish("需要内容")
    try:
        msg: str = decode(arg.encode()).decode()
    except KeyError as e:
        logger.error(repr(e))
        await de64Gua.finish("格式错误: 不是有效的卦象文本")
    except UnicodeDecodeError as e:
        logger.error(repr(e))
        await de64Gua.finish("解码失败: 无法转换成有效的utf-8字符串文本")
    if not msg:
        await de64Gua.finish("解码成功, 但是文本为空")

    gid: int = event.group_id if isinstance(event, GroupMessageEvent) else 0
    uid: int = event.user_id if not gid else 0
    node = [MessageSegment.node_custom(
        event.user_id,
        event.sender.card or event.sender.nickname or "老色批",
        msg
    )]
    try:
        await bot.send_forward_msg(
            user_id=uid, group_id=gid, messages=node)
    except ActionFailed as e:
        logger.error(repr(e))
        await de64Gua.finish(err_info(e))


def err_info(e: ActionFailed) -> str:
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)
