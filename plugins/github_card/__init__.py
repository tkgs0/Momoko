from nonebot import on_message
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageSegment,
    unescape
)
import re
from .data_source import (
    get_github_reposity_information,
    get_url,
)


__plugin_meta__ = PluginMetadata(
    name="Github卡片",
    description="Github仓库信息卡片",
    usage="被动触发",
    type="application"
)


github = on_message(priority=5, block=False)


@github.handle()
async def github_handle(event: GroupMessageEvent):
    text = unescape(event.get_plaintext())
    if res := re.search(r"github\.com/[^/]+/[^/\s]+", text):
        url = res.group()
        imageUrl = await get_github_reposity_information(url)
        assert(imageUrl != "获取信息失败")
        await github.send(MessageSegment.image(await get_url(imageUrl), cache=False))
        # await github.finish(MessageSegment.image(await get_url(f"https://image.thum.io/get/width/1280/crop/1440/viewportWidth/1280/png/noanimate/https://{url}"), cache=False))
