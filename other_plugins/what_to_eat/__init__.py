import random
from time import time
from typing import List, Tuple
from pathlib import Path
import ujson as json
from httpx import AsyncClient
from nonebot import logger, on_regex, on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    MessageEvent,
    GroupMessageEvent,
)


__help__: str = """

查看吃库

添加到吃库 [图片]

从吃库删除 文件名

吃什么

""".strip()


imgdir: Path = Path(__file__).parent / "resource"
imgs: list[Path] = [ i for i in imgdir.rglob(r'*.*') ]

filepath: Path = Path() / "data" / "what_to_eat" / "eat.json"
filepath.parent.mkdir(parents=True, exist_ok=True)

records: dict = (
    json.loads(filepath.read_text("utf-8"))
    if filepath.is_file()
    else {"user": {}}
)


def save_file() -> None:
    filepath.write_text(
        json.dumps(records, indent=2, ensure_ascii=False), "utf-8")


eat = on_regex(
    r'[.\s]*((喫|吃)(啥|什|甚)(么|麼)?|食乜(嘢)?)\s*$',
    priority=15,
    block=False
)

@eat.handle()
async def _(event: MessageEvent):
    _time = time()
    uid = str(event.user_id)
    user = records["user"].get(uid)
    if user and _time - user[1] < 600:
        img = imgdir / user[0]
    else:
        img = get_img(uid, _time)

    while not img.is_file():
        clean_list(img)
        img = get_img(uid, _time)

    await eat.finish(MessageSegment.image(img.read_bytes()))


def clean_list(img: Path) -> None:
    try:
        imgs.remove(img)
    except ValueError:
        pass

def get_img(uid: str, _time: float) -> Path:
    img = random.choice(imgs)
    records["user"][uid] = [img.name, _time]
    save_file()
    return img


see_imgs = on_command(
    "查看吃库",
    aliases={"浏览吃库"},
    permission=SUPERUSER,
    priority=5,
    block=True
)

@see_imgs.handle()
async def _(bot: Bot, event: MessageEvent):

    gid: int = event.group_id if isinstance(event, GroupMessageEvent) else 0
    uid: int = event.user_id if not gid else 0

    name = event.sender.nickname
    node: list = [{
        "type": "node",
        "data": {
            "name": name if name else "老色批",
            "uin": event.user_id,
            "content": f'{MessageSegment.image(i, cache=False)}\n{i.name}'
        }
    } for i in imgs]
    await bot.send_forward_msg(user_id=uid, group_id=gid, messages=node)


del_img = on_command(
    "从吃库删除",
    permission=SUPERUSER,
    priority=5,
    block=True
)

@del_img.handle()
async def _(
    matcher: Matcher,
    args: Message = CommandArg()
):
    msg: str = args.extract_plain_text()
    if msg:
        matcher.set_arg('ARGS', args)

@del_img.got("ARGS", prompt="需要文件名")
async def _(args: str = ArgPlainText('ARGS')):
    files = args.split()
    if not files:
        await del_img.reject()
    for i in files:
        file = imgdir / i
        file.unlink(missing_ok=True)
        clean_list(file)
    await del_img.finish(f"已尝试删除{len(files)}个文件.")


add_img = on_command(
    "添加到吃库",
    permission=SUPERUSER,
    priority=5,
    block=True
)

@add_img.handle()
async def _(event: MessageEvent, matcher: Matcher) -> None:
    if contains_image(event):
        matcher.state["IMAGES"] = event

@add_img.got("IMAGES", prompt="图呢?")
async def _(event: MessageEvent) -> None:
    image_urls = get_image_urls(event)
    if not image_urls:
        await add_img.send("图呢?")
        await add_img.reject()
    imglist, status = await image_download(image_urls)
    imgs.extend([ i for i in imglist if i not in imgs ])
    await add_img.finish(f"下载完毕:\n{len(imglist)}个成功, {len(status)}个失败")


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

