import asyncio
from io import BytesIO
from httpx import AsyncClient
from nonebot import logger, require
require("nonebot_plugin_imageutils")
from nonebot_plugin_imageutils import BuildImage as Image


def edit_img(img: bytes) -> BytesIO:
    image = Image.open(BytesIO(img))
    # image.draw_ellipse((5,5,50,50), outline='red')
    image = image.resize_width(image.width // 2)
    return image.save_png()


async def down_pic(content, pixproxy) -> tuple[list, list]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    if not pixproxy:
        headers = {
            'Host': 'i.pximg.net',
            'Referer': 'https://www.pixiv.net/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

    down, imgs, status = [], {}, {}

    async def dload(sem, i):
        async with sem:
            async with AsyncClient() as client:
                res = await client.get(
                    url = (
                        i['url'].replace(
                            'https://i.pximg.net', pixproxy
                        ).replace(
                            'https://i.pixiv.re', pixproxy
                        )
                        if pixproxy
                        else i['url'].replace('i.pixiv.re', 'i.pximg.net')
                    ),
                    headers=headers,
                    timeout=30
                )
                if res.status_code == 200:
                    imgs[i["pid"]] = [edit_img(res.content), i['caption']]
                    logger.success(f'获取图片 {i["pid"]} 成功')
                else:
                    status[i["pid"]] = f'获取图片 {i["pid"]} 失败: {res.status_code}'
                    logger.error(status[i["pid"]])
                await res.aclose()

    sem = asyncio.Semaphore(16)
    for i in content:
        down.append(dload(sem, i))
    await asyncio.gather(*down)

    return list(imgs.values()), list(status.values())

