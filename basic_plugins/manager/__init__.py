from pathlib import Path
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment
from . import (
    bot_id,
    group_manage,
    request_manage,
    friend_group,
    withdraw,
    keyword_ban,
)


usage = f'{MessageSegment.image(Path(__file__).parent / "manager_help.png")}'


__plugin_meta__ = PluginMetadata(
    name="管理",
    description="好友/群聊管理插件",
    usage=usage,
    type="application"
)
