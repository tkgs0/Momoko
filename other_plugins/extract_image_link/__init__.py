from pathlib import Path
from typing import List, Tuple
from httpx import AsyncClient
from nonebot import on_keyword, logger, get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    ActionFailed
)
from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    extract_images_path: str | Path = Path() / "extracted_images"


usage: str = r"""
如需自定义图片保存路径:
  在 Bot目录/.env 里添加变量 EXTRACT_IMAGES_PATH
  示例: EXTRACT_IMAGES_PATH="C:\setu"

指令表:
  提取图片[图片]
""".strip()


__plugin_meta__ = PluginMetadata(
    name="提取图片",
    description="发送表情包消息回复图片消息(仅限自定义表情)",
    usage=usage,
    type="application"
)


extract_images_path = get_plugin_config(Config).extract_images_path
imgdir: Path = Path(extract_images_path)
imgdir.mkdir(parents=True, exist_ok=True)


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
    imglist, status = await image_download(image_urls)

    msg = Message(
        "\n".join([
            f"{MessageSegment.image(i,cache=False)}\n本地路径: {i}"
            for i in imglist
        ]) +\
        f"\n\n下载完毕:\n{len(imglist)}个成功, {len(status)}个失败"
    )
    try:
        await extract.finish(msg)
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


async def image_download(
    imglist: List[Tuple[str,str]]
) -> Tuple[List[Path], List[str]]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    pics, status = [], []
    for i in imglist:
        async with AsyncClient().stream(
            "GET", url = i[0],
            headers=headers,
            follow_redirects=True,
            timeout=30
        ) as res:
            if res.status_code == 200:
                img = imgdir / i[1]
                with open(img, 'wb') as fd:  # 写入文件
                    async for chunk in res.aiter_bytes(1024):
                        fd.write(chunk)
                logger.success(f'获取图片 {i[1]} 成功')
                pics.append(img)
            else:
                logger.error(sc := f'获取图片 {i[1]} 失败: {res.status_code}')
                status.append(sc)
            await res.aclose()
    return pics, status
