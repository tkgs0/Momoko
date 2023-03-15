import asyncio
import re
from collections import defaultdict
from contextlib import suppress
from typing import Any, DefaultDict, Dict, List, Optional, Tuple, Union

import arrow
from aiohttp import ClientSession
from cachetools import TTLCache
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
from shelved_cache import PersistentCache
from tenacity import retry, stop_after_attempt, stop_after_delay

from .ascii2d import ascii2d_search
from .baidu import baidu_search
from .config import config
from .ehentai import ehentai_search
from .iqdb import iqdb_search
from .saucenao import saucenao_search
from .utils import (
    DEFAULT_HEADERS,
    SEARCH_FUNCTION_TYPE,
    get_bot_friend_list,
    handle_reply_msg,
)

sending_lock: DefaultDict[Tuple[Union[int, str], str], asyncio.Lock] = defaultdict(
    asyncio.Lock
)
pic_search_cache = PersistentCache(
    TTLCache,
    filename="pic_search_cache",
    maxsize=config.cache_expire * 100,
    ttl=config.cache_expire * 24 * 60 * 60,
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


def message_needs_handling(bot: Bot, event: MessageEvent) -> bool:
    plain_text = event.message.extract_plain_text().strip()
    # 有搜图关键词必响应
    if re.search(rf"^{config.search_keyword}(\s+)?(--\w+)?$", plain_text):
        return True
    elif (
        config.search_keyword_only
        or (not contains_image(event))
        # 回复机器人发送的消息时，必须带上搜图关键词才会搜图，否则会被无视
        or (event.reply and event.reply.sender.user_id == int(bot.self_id))
    ):
        return False

    if isinstance(event, PrivateMessageEvent):
        return config.search_immediately

    # @机器人 如果在消息开头或结尾会被截去，并且 event.to_me 设为 True ，这里针对 @机器人 在消息中间的情况做处理
    to_me = any(i.type == "at" and i.data["qq"] == bot.self_id for i in event.message)
    return event.to_me or to_me


IMAGE_SEARCH = on_message(rule=Rule(message_needs_handling), priority=5)


@IMAGE_SEARCH.handle()
async def handle_first_receive(event: MessageEvent, matcher: Matcher) -> None:
    mode, purge = get_args(event.message)
    matcher.state["ARGS"] = (mode, purge)
    if contains_image(event):
        matcher.state["IMAGES"] = event


async def image_search(
    bot: Bot,
    event: MessageEvent,
    url: str,
    md5: str,
    mode: str,
    purge: bool,
    client: ClientSession,
    index: Optional[int] = None,
) -> None:
    url = await get_universal_img_url(url)
    cache_key = f"{md5}_{mode}"
    try:
        if not purge and cache_key in pic_search_cache:
            result, extra_handle = pic_search_cache[cache_key]
            await send_result_message(bot, event, [f"[缓存] {i}" for i in result], index)
            if callable(extra_handle):
                await send_result_message(
                    bot, event, await extra_handle(url, client), index
                )
            return

        result, extra_handle = await handle_search_mode(url, md5, mode, client)
        await send_result_message(bot, event, result, index)
        if callable(extra_handle):
            await send_result_message(
                bot, event, await extra_handle(url, client), index
            )
    except Exception as e:
        logger.exception(f"该图 [{url}] 搜图失败")
        await send_result_message(bot, event, [f"该图搜图失败\nE: {repr(e)}"], index)


@retry(stop=(stop_after_attempt(3) | stop_after_delay(30)), reraise=True)
async def handle_search_mode(
    url: str, md5: str, mode: str, client: ClientSession
) -> Tuple[List[str], Optional[SEARCH_FUNCTION_TYPE]]:
    extra_handle = None

    if mode == "a2d":
        result = await ascii2d_search(url, client)
    elif mode == "ex":
        result, extra_handle = await ehentai_search(url, client)
    elif mode == "iqdb":
        result, extra_handle = await iqdb_search(url, client)
    elif mode == "baidu":
        result = await baidu_search(url, client)
    else:
        result, extra_handle = await saucenao_search(url, client, mode)

    pic_search_cache[f"{md5}_{mode}"] = result, extra_handle

    return result, extra_handle


async def get_universal_img_url(url: str) -> str:
    final_url = url.replace(
        "/c2cpicdw.qpic.cn/offpic_new/", "/gchat.qpic.cn/gchatpic_new/"
    )
    final_url = re.sub(r"/\d+/+\d+-\d+-", "/0/0-0-", final_url)
    final_url = re.sub(r"\?.*$", "", final_url)
    async with ClientSession(headers=DEFAULT_HEADERS) as session:
        async with session.get(final_url) as resp:
            if resp.status < 400:
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
    if not (
        isinstance(event, PrivateMessageEvent)
        and event.user_id == int(list(config.superusers)[0])
    ):
        msg_list = [
            msg.replace("❤️ 已收藏\n", "") if "已收藏" in msg else msg for msg in msg_list
        ]

    if isinstance(event, GroupMessageEvent):
        current_sending_lock = sending_lock[(event.group_id, "group")]
    else:
        current_sending_lock = sending_lock[(event.user_id, "private")]

    if flag := (config.forward_search_result and len(msg_list) > 1):
        try:
            await send_message_with_lock(
                bot, event, msg_list, current_sending_lock, index
            )
        except ActionFailed:
            flag = False
    if not flag:
        for msg in msg_list:
            await send_message_with_lock(bot, event, [msg], current_sending_lock, index)


async def send_message_with_lock(
    bot: Bot,
    event: MessageEvent,
    msg_list: List[str],
    current_sending_lock: asyncio.Lock,
    index: Optional[int] = None,
) -> None:
    start_time = arrow.now()
    async with current_sending_lock:
        if len(msg_list) == 1:
            await send_msg(bot, event, msg_list[0], index)
        else:
            await send_forward_msg(bot, event, msg_list, index)
        await asyncio.sleep(max(1 - (arrow.now() - start_time).total_seconds(), 0))


async def send_msg(
    bot: Bot, event: MessageEvent, message: str, index: Optional[int] = None
) -> None:
    group_id=event.group_id if isinstance(event, GroupMessageEvent) else 0
    user_id=event.user_id if not group_id else 0

    if index:
        message = f"第 {index + 1} 张图片的搜索结果：\n{message}"
    message = f"{handle_reply_msg(event.message_id)}{message}"
    try:
        await bot.send_forward_msg(
            user_id=user_id,
            group_id=group_id,
            messages=[{
                "type": "node",
                "data": {
                    "name": event.sender.card or event.sender.nickname or '老色批',
                    "uin": event.user_id,
                    "content": message
                }
            }]
        )
    except ActionFailed as e:
        await bot.send(event=event, message=err_info(e))


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
    group_id=event.group_id if isinstance(event, GroupMessageEvent) else 0
    user_id=event.user_id if not group_id else 0

    if index:
        msg_list = [f"第 {index + 1} 张图片的搜索结果："] + msg_list
    try:
        await bot.send_forward_msg(
            user_id=user_id,
            group_id=group_id,
            messages=[{
                "type": "node",
                "data": {
                    "name": event.sender.card or event.sender.nickname or '老色批',
                    "uin": event.user_id,
                    "content": msg,
                }
            } for msg in msg_list]
        )
    except ActionFailed as e:
        await bot.send(event=event, message=err_info(e))


@IMAGE_SEARCH.got("IMAGES", prompt="请发送图片")
async def handle_image_search(bot: Bot, event: MessageEvent, matcher: Matcher) -> None:
    image_urls_with_md5 = get_image_urls_with_md5(event)
    if not image_urls_with_md5:
        await IMAGE_SEARCH.reject()

    searching_tips: Dict[str, Any] = await IMAGE_SEARCH.send(
        "正在进行搜索，请稍候", reply_message=True
    )

    mode, purge = matcher.state["ARGS"]
    network = (
        Network(proxies=config.proxy, cookies=config.exhentai_cookies, timeout=60)
        if mode == "ex"
        else Network(proxies=config.proxy)
    )
    async with network as client:
        for index, (url, md5) in enumerate(image_urls_with_md5):
            await image_search(
                bot,
                event,
                url,
                md5,
                mode,
                purge,
                client,
                index if len(image_urls_with_md5) > 1 else None,
            )

    await bot.delete_msg(message_id=searching_tips["message_id"])
