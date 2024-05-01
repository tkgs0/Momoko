from typing import List, Tuple
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent


usage: str = """

指令表:
  提取链接[图片]
""".strip()


__plugin_meta__ = PluginMetadata(
    name="提取图片链接",
    description="用于提取表情包图片",
    usage=usage,
    type="application"
)


extract = on_command(
    "提取链接",
    aliases={"提取鏈接"},
    permission=SUPERUSER,
    priority=5,
    block=True
)


@extract.handle()
async def _(event: MessageEvent, matcher: Matcher) -> None:
    if contains_image(event):
        matcher.state["IMAGES"] = event

@extract.got("IMAGES", prompt="图呢?")
async def _(event: MessageEvent) -> None:
    image_urls = get_image_urls(event)
    if not image_urls:
        await extract.send("图呢?")
        await extract.reject()
    msg = "\n".join([i[0] for i in image_urls])
    await extract.finish(msg)


def contains_image(event: MessageEvent) -> bool:
    message = event.reply.message if event.reply else event.message
    return bool([i for i in message if i.type == "image"])


def get_image_urls(event: MessageEvent) -> List[Tuple[str, str]]:
    message = event.reply.message if event.reply else event.message
    return [
        (i.data["url"], str(i.data["file"]).upper())
        for i in message
        if i.type == "image" and i.data.get("url")
    ]
