from pathlib import Path
from nonebot.plugin import on_command, PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from . import (
    bot_id,
    group_manage,
    request_manage,
    friend_group,
    withdraw,
    keyword_ban,
)


__plugin_meta__ = PluginMetadata(
    name="管理",
    description="好友/群聊管理插件",
    usage="发送 manager.help 查看帮助",
    type="application"
)


m = on_command("mamager", priority=2, block=False)

@m.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text().strip() == ".help":
        await m.finish(MessageSegment.image(Path(__file__).parent / "manager_help.png", cache=False))
