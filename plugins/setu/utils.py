from io import BytesIO
from httpx import AsyncClient
from nonebot import logger, require
require("nonebot_plugin_imageutils")
from nonebot_plugin_imageutils import BuildImage as Image


def edit_img(img: bytes) -> bytes:
    image = Image.open(BytesIO(img))
    image = image.resize_width(image.width//2 if image.width < 4000 else 1000)
    return image.save_png().getvalue()


async def down_pic(content, pixproxy) -> tuple[list, list]:
    async with AsyncClient() as client:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }
        if not pixproxy:
            headers = {
                'Host': 'i.pximg.net',
                'Referer': 'https://www.pixiv.net/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
            }
        pics, status = list(), list()
        for i in content:
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
                logger.success(f'获取图片 {i["pid"]} 成功')
                pics.append([edit_img(res.content), i['caption']])
            else:
                logger.error(sc := f'获取图片 {i["pid"]} 失败: {res.status_code}')
                status.append(sc)
            await res.aclose()
        return pics, status

