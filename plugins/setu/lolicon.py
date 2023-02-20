from sys import exc_info
import httpx
from httpx import AsyncClient
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .utils import down_pic


async def get_setu(
    uid: int,
    name: str,
    keyword: list = [],
    img: int = 1,
    pixproxy: str = '',
    r18: int = 0,
    **kwargs
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
            logger.error(e)
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

            logger.info('complete.')

            if not pics:
                return ['\n'.join(status), False]

            node = [{
                "type": "node",
                "data": {
                    "name": name,
                    "uin": str(uid),
                    "content": '\n'.join([
                        f'{MessageSegment.image(i[0], cache=False)}\n{i[1]}'
                        for i in pics
                    ])
                }
            }]

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
            logger.error(e)
            return [f'代理错误: {e}', False]
        except IndexError as e:
            logger.warning(e)
            return [f'图库中没有搜到关于{keyword}的图。', False]
        except:
            logger.exception(f'{exc_info()[0]}, {exc_info()[1]}')
            return [f'{exc_info()[0]} {exc_info()[1]}。', False]

