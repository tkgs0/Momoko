import random
from time import time
from pathlib import Path
import ujson as json
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
    MessageEvent,
)


imgdir: Path = Path(__file__).parent / "resource"
imgs: list[Path] = [ i for i in imgdir.rglob(r'*.*png') ]

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

    if user and _time - user[1] < 600 and (img := imgdir / user[0]).is_file():
        img = img
    else:
        img: Path = random.choice(imgs)
        records["user"][uid] = [img.name, _time]
        save_file()

    await eat.finish(MessageSegment.image(img.read_bytes()))
    
