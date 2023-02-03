from nonebot import on_message, get_driver
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageSegment,
    unescape
)
import re
from .config import Config
from .data_source import (
    get_github_reposity_information,
    get_url,
)


__plugin_name__ = "Github仓库信息卡片"


global_config = get_driver().config
config = Config(**global_config.dict())
github = on_message(priority=5, block=False)


@github.handle()
async def github_handle(event: GroupMessageEvent):
    url = unescape(event.get_plaintext())
    if re.match("https://github.com/.*?/.*?", url):
        imageUrl = await get_github_reposity_information(url)
        assert(imageUrl != "获取信息失败")
        await github.send(MessageSegment.image(await get_url(imageUrl)))
        await github.finish(MessageSegment.image(await get_url(f"https://image.thum.io/get/width/1280/crop/1440/viewportWidth/1280/png/noanimate/{url}")))
