from sys import exc_info
import httpx
from httpx import AsyncClient

from nonebot import require
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment

require("nonebot_plugin_imageutils")
from nonebot_plugin_imageutils import BuildImage as Image


def edit_img(img: bytes) -> bytes:
    image = Image.open(img)
    image.draw_ellipse((3,3,30,30), outline='black')
    return image.save_png().getvalue()


async def get_setu(
    uid: int,
    name: str,
    keyword: list = [],
    img: int = 1,
    pixproxy: str = '',
    r18: int = 0,
) -> list:
    logger.info('loading...')
    async with AsyncClient() as client:
        req_url = 'https://api.lolicon.app/setu/v2'
        params = {
            'tag': keyword,
            'r18': r18,
            'size': 'regular',
            'num': img if img < 11 else 1
        }
        try:
            res = await client.get(req_url, params=params, timeout=30)
        except httpx.HTTPError as e:
            logger.warning(e)
            return [f'API异常{e}', False]
        try:
            logger.debug(content := res.json()['data'])
            _ = content[0]

            content = [{
                'pid': i['pid'],
                'url': i['urls']['regular'],
                'caption': (
                    f'标题: {i["title"]}\n'
                    f'pid: {i["pid"]}\n'
                    f'画师: {i["author"]}\n'
                    f'标签: {", ".join(i["tags"])}'
                )
            } for i in content]

            pics, status = await down_pic(content, pixproxy)

            logger.success('complete.')

            if not pics:
                return ['\n'.join(status), False]

            node = [
                {
                    "type": "node",
                    "data": {
                        "name": name,
                        "uin": str(uid),
                        "content": f'{MessageSegment.image(i[0])}\n{i[1]}'
                    }
                }
                for i in pics
            ]

            if status:
                node.append({
                    "type": "node",
                    "data": {
                        "name": name,
                        "uin": str(uid),
                        "content": '\n'.join(status)
                    }
                })

            return [node, 1]

        except httpx.ProxyError as e:
            logger.warning(e)
            return [f'代理错误: {e}', False]
        except IndexError as e:
            logger.warning(e)
            return [f'图库中没有搜到关于{keyword}的图。', False]
        except:
            logger.warning(f'{exc_info()[0]}, {exc_info()[1]}')
            return [f'{exc_info()[0]} {exc_info()[1]}。', False]



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
                    i['url'].replace('https://i.pixiv.re', pixproxy)
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

