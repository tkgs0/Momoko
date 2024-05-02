from typing import List, Tuple
from nonebot import on_keyword, logger
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    ActionFailed
)


usage: str = """

指令表:
  提取图片[图片]
""".strip()


__plugin_meta__ = PluginMetadata(
    name="提取图片",
    description="发送表情包消息回复图片消息(仅限自定义表情)",
    usage=usage,
    type="application"
)


extract = on_keyword(
    {"提取图片", "提取圖片"},
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
    try:
        await extract.finish(Message([MessageSegment.image(i[0], cache=False) for i in image_urls]))
    except ActionFailed as e:
        err_info(e)
        try:
            await extract.finish("\n\n".join([i[0] for i in image_urls]))
        except ActionFailed as e:
            await extract.finish(err_info(e))


def err_info(e: ActionFailed) -> str:
    logger.error(repr(e))
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)


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
