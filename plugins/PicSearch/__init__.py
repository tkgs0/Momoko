import asyncio
import re
from collections import defaultdict
from contextlib import suppress
from typing import DefaultDict, List, Optional, Tuple, Union

import arrow
from aiohttp import ClientSession
from diskcache import Cache
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    Bot,
    GroupMessageEvent,
    LifecycleMetaEvent,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.plugin.on import on_message, on_metaevent
from nonebot.rule import Rule
from PicImageSearch import Network
from tenacity import AsyncRetrying, stop_after_attempt, stop_after_delay

from .ascii2d import ascii2d_search
from .baidu import baidu_search
from .cache import exist_in_cache, upsert_cache
from .config import config
from .ehentai import ehentai_search
from .iqdb import iqdb_search
from .saucenao import saucenao_search
from .utils import DEFAULT_HEADERS, get_bot_friend_list, handle_img, handle_reply_msg

sending_lock: DefaultDict[Tuple[Union[int, str], str], asyncio.Lock] = defaultdict(
    asyncio.Lock
)


def check_first_connect(_: LifecycleMetaEvent) -> bool:
    return True


start_metaevent = on_metaevent(rule=check_first_connect, temp=True)


@start_metaevent.handle()
async def _(bot: Bot) -> None:
    if not config.saucenao_api_key:
        await bot.send_private_msg(
            user_id=int(list(config.superusers)[0]),
            message="请配置 saucenao_api_key ，否则无法正常使用搜图功能",
        )


def contains_image(event: MessageEvent) -> bool:
    message = event.reply.message if event.reply else event.message
    return bool([i for i in message if i.type == "image"])


def to_me_with_image_or_command(bot: Bot, event: MessageEvent) -> bool:
    plain_text = event.message.extract_plain_text().strip()
    if command_exists := re.search(r"^搜图(\s+)?(--\w+)?$", plain_text):
        return True
    image_exists = contains_image(event)
    if isinstance(event, PrivateMessageEvent):
        return image_exists and config.search_immediately
    # 群里回复机器人发送的消息时，必须带上 "搜图" 才会搜图，否则会被无视
    if event.reply and event.to_me:
        return image_exists and command_exists
    at_me = bool(
        [i for i in event.message if i.type == "at" and i.data["qq"] == bot.self_id]
    )
    return image_exists and at_me


IMAGE_SEARCH = on_message(rule=Rule(to_me_with_image_or_command), priority=5)


@IMAGE_SEARCH.handle()
async def handle_first_receive(event: MessageEvent, matcher: Matcher) -> None:
    mode, purge = get_args(event.message)
    matcher.state["ARGS"] = (mode, purge)
    if contains_image(event):
        matcher.state["IMAGES"] = event


async def image_search(
    url: str,
    md5: str,
    mode: str,
    purge: bool,
    _cache: Cache,
    client: ClientSession,
    hide_img: bool = config.hide_img,
) -> List[str]:
    url = await get_universal_img_url(url)
    if not purge and (result := exist_in_cache(_cache, md5, mode)):
        return [f"[缓存] {i}" for i in result]
    result = []
    try:
        async for attempt in AsyncRetrying(
            stop=(stop_after_attempt(3) | stop_after_delay(30)), reraise=True
        ):
            with attempt:
                if mode == "a2d":
                    result = await ascii2d_search(url, client, hide_img)
                elif mode == "ex":
                    result = await ehentai_search(url, client, hide_img)
                elif mode == "iqdb":
                    result = await iqdb_search(url, client, hide_img)
                elif mode == "baidu":
                    result = await baidu_search(url, client, hide_img)
                else:
                    result = await saucenao_search(url, mode, client, hide_img)
                    # 仅对涉及到 saucenao 的搜图结果做缓存
                    upsert_cache(_cache, md5, mode, result)
    except Exception as e:
        logger.exception(f"该图 [{url}] 搜图失败")
        result = [f"该图搜图失败\nE: {repr(e)}"]
    return result


async def get_universal_img_url(url: str) -> str:
    final_url = url.replace(
        "/c2cpicdw.qpic.cn/offpic_new/", "/gchat.qpic.cn/gchatpic_new/"
    )
    final_url = re.sub(r"/\d+/+\d+-\d+-", "/0/0-0-", final_url)
    final_url = re.sub(r"\?.*$", "", final_url)
    async with ClientSession(headers=DEFAULT_HEADERS) as session:
        async with session.get(final_url) as resp:
            if resp.status == 200:
                return final_url
    return url


def get_image_urls_with_md5(event: MessageEvent) -> List[Tuple[str, str]]:
    message = event.reply.message if event.reply else event.message
    return [
        (i.data["url"], str(i.data["file"]).rstrip(".image").upper())
        for i in message
        if i.type == "image" and i.data.get("url")
    ]


def get_args(msg: Message) -> Tuple[str, bool]:
    mode = "all"
    plain_text = msg.extract_plain_text().strip()
    args = ["pixiv", "danbooru", "doujin", "anime", "a2d", "ex", "iqdb", "baidu"]
    if plain_text:
        for i in args:
            if f"--{i}" in plain_text:
                mode = i
                break
    purge = "--purge" in plain_text
    return mode, purge


async def send_result_message(
    bot: Bot, event: MessageEvent, msg_list: List[str], index: Optional[int] = None
) -> None:
    if isinstance(event, GroupMessageEvent):
        current_sending_lock = sending_lock[(event.group_id, "group")]
    else:
        current_sending_lock = sending_lock[(event.user_id, "private")]
    if flag := (config.forward_search_result and len(msg_list) > 1):
        try:
            start_time = arrow.now()
            async with current_sending_lock:
                await send_forward_msg(bot, event, msg_list, index)
                await asyncio.sleep(
                    max(1 - (arrow.now() - start_time).total_seconds(), 0)
                )
        except ActionFailed:
            flag = False
    if not flag:
        for msg in msg_list:
            start_time = arrow.now()
            async with current_sending_lock:
                await send_msg(bot, event, msg, index)
                await asyncio.sleep(
                    max(1 - (arrow.now() - start_time).total_seconds(), 0)
                )


async def send_msg(
    bot: Bot, event: MessageEvent, message: str, index: Optional[int] = None
) -> None:
    user_id=event.user_id if isinstance(event, PrivateMessageEvent) else 0
    group_id=event.group_id if isinstance(event, GroupMessageEvent) else 0

    if index:
        message = f"第 {index + 1} 张图片的搜索结果：\n{message}"
    message = f"{handle_reply_msg(event.message_id)}{message}"
    try:
        result = await bot.send_forward_msg(
            user_id=user_id,
            group_id=group_id,
            messages=[{
                "type": "node",
                "data": {
                    "name": (event.sender.nickname
                             if event.sender.nickname
                             else '老色批'),
                    "uin": event.user_id,
                    "content": message
                }
            }]
        )
        del_msg(bot, result['message_id'])
    except ActionFailed as e:
        await bot.send_msg(
            user_id=user_id,
            group_id=group_id,
            message=err_info(e),
        )


def del_msg(bot: Bot, mid: int):
    from random import random
    loop = asyncio.get_running_loop()
    loop.call_later(
        60 + random()*3-1,  # 消息撤回等待时间 单位秒
        lambda: loop.create_task(bot.delete_msg(message_id=mid)),
    )


def err_info(e: ActionFailed) -> str:
    logger.error(repr(e))
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)


async def send_forward_msg(
    bot: Bot, event: MessageEvent, msg_list: List[str], index: Optional[int] = None
) -> None:
    user_id=event.user_id if isinstance(event, PrivateMessageEvent) else 0
    group_id=event.group_id if isinstance(event, GroupMessageEvent) else 0

    if index:
        msg_list = [f"第 {index + 1} 张图片的搜索结果："] + msg_list
    try:
        result = await bot.send_forward_msg(
            user_id=user_id,
            group_id=group_id,
            messages=[{
                "type": "node",
                "data": {
                    "name": (event.sender.nickname
                             if event.sender.nickname
                             else '老色批'),
                    "uin": event.user_id,
                    "content": msg,
                }
            } for msg in msg_list]
        )
        del_msg(bot, result['message_id'])
    except ActionFailed as e:
        await bot.send_msg(
            user_id=user_id,
            group_id=group_id,
            message=err_info(e),
        )


@IMAGE_SEARCH.got("IMAGES", prompt="请发送图片")
async def handle_image_search(bot: Bot, event: MessageEvent, matcher: Matcher) -> None:
    image_urls_with_md5 = get_image_urls_with_md5(event)
    if not image_urls_with_md5:
        await IMAGE_SEARCH.reject()

    await IMAGE_SEARCH.send("正在搜索，请稍候～")

    mode, purge = matcher.state["ARGS"]
    network = (
        Network(proxies=config.proxy, cookies=config.exhentai_cookies, timeout=60)
        if mode == "ex"
        else Network(proxies=config.proxy)
    )
    async with network as client:
        with Cache("picsearch_cache") as _cache:
            for index, (url, md5) in enumerate(image_urls_with_md5):
                await send_result_message(
                    bot,
                    event,
                    await image_search(url, md5, mode, purge, _cache, client),
                    index if len(image_urls_with_md5) > 1 else None,
                )
            _cache.expire()
