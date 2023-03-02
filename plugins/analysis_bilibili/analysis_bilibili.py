import json
import re
import urllib.parse
from time import localtime, strftime
from typing import Dict, Match, Optional, Tuple, Union

import aiohttp
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger

from .config import config

MINI_APP_REGEX = re.compile(r'"desc":("[^"哔哩]+")', re.I)
B23_REGEX = re.compile(r"b23.tv/(\w+)|(bili(22|23|33|2233).cn)/(\w+)", re.I)
EPID_REGEX = re.compile(r"ep_id=(\d+)", re.I)
REGEX_PATTERNS: Dict[str, re.Pattern[str]] = {
    "page": re.compile(r"([?&]|&amp;)p=\d+", re.I),  # 视频分p
    "time_location": re.compile(r"([?&]|&amp;)t=\d+", re.I),  # 视频播放定位时间
    "aid": re.compile(r"av(\d+)", re.I),  # 主站视频 av 号
    "bvid": re.compile(r"BV([a-z\d]{10})+", re.I),  # 主站视频 bv 号
    "epid": re.compile(r"ep(\d+)", re.I),  # 番剧视频页
    "ssid": re.compile(r"ss(\d+)", re.I),  # 番剧剧集ssid(season_id)
    "mdid": re.compile(r"md(\d+)", re.I),  # 番剧详细页
    "room_id": re.compile(r"live.bilibili.com/(blanc/|h5/)?(\d+)", re.I),  # 直播间
    "cvid": re.compile(r"(/read/(cv|mobile|native)(/|\?id=)?|^cv)(\d+)", re.I),  # 文章
    "dynamic_id_type2": re.compile(
        r"([tm]).bilibili.com/(\d+)\?(.*?)(&|&amp;)type=2", re.I
    ),  # 动态
    "dynamic_id": re.compile(r"([tm]).bilibili.com/(\d+)", re.I),  # 动态
}
MATCHED_URLS: Dict[str, str] = {
    "aid": "https://api.bilibili.com/x/web-interface/view?aid={}",
    "bvid": "https://api.bilibili.com/x/web-interface/view?bvid={}",
    "epid": "https://bangumi.bilibili.com/view/web_api/season?ep_id={}",
    "ssid": "https://bangumi.bilibili.com/view/web_api/season?season_id={}",
    "mdid": "https://bangumi.bilibili.com/view/web_api/season?media_id={}",
    "room_id": "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={}",
    "cvid": "https://api.bilibili.com/x/article/viewinfo?id={}&mobi_app=pc&from=web",
    "dynamic_id_type2": "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?rid={}&type=2",
    "dynamic_id": "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={}",
}
# group_id : last_vurl
analysis_stat: Dict[int, str] = {}


async def bili_keyword(group_id: Optional[int], text: str) -> Union[Message, str]:
    try:
        # 提取url
        url, page, time_location = extract(text)
        # 如果是小程序就去搜索标题
        if not url:
            if title := MINI_APP_REGEX.search(text):
                if vurl := await search_bili_by_title(title[1]):
                    url, page, time_location = extract(vurl)

        # 获取视频详细信息
        if "view?" in url:
            msg, vurl = await video_detail(url, page=page, time_location=time_location)
        elif "bangumi" in url:
            msg, vurl = await bangumi_detail(url, time_location)
        elif "xlive" in url:
            msg, vurl = await live_detail(url)
        elif "article" in url:
            msg, vurl = await article_detail(url, page)  # type: ignore
        elif "dynamic" in url:
            msg, vurl = await dynamic_detail(url)
        else:
            msg = vurl = ""

        # 避免多个机器人解析重复推送
        if group_id:
            if group_id in analysis_stat and analysis_stat[group_id] == vurl:
                return ""
            analysis_stat[group_id] = vurl
    except Exception as e:
        logger.exception(e)
        msg = f"bili_keyword Error: {type(e)}"
    return msg


async def b23_extract(text: str) -> str:
    b23 = B23_REGEX.search(text.replace("\\", ""))
    url = f"https://{b23[0]}"  # type: ignore
    async with aiohttp.request("GET", url) as resp:
        return str(resp.url)


def extract(text: str) -> Tuple[str, Optional[Match[str]], Optional[Match[str]]]:
    url = ""
    page: Optional[Match[str]] = None
    time_location: Optional[Match[str]] = None

    try:
        for key, pattern in REGEX_PATTERNS.items():
            if match := pattern.search(text):
                if key == "bvid":
                    url = MATCHED_URLS[key].format(match[0])
                elif key in ["aid", "epid", "ssid", "mdid"]:
                    url = MATCHED_URLS[key].format(match[1])
                elif key in ["room_id", "dynamic_id_type2", "dynamic_id"]:
                    url = MATCHED_URLS[key].format(match[2])
                elif key == "cvid":
                    page = match[4]  # type: ignore
                    url = MATCHED_URLS[key].format(page)
                else:
                    if key == "page":
                        page = match
                    elif key == "time_location":
                        time_location = match

        return url, page, time_location

    except Exception as e:
        logger.exception(e)
        return "", None, None


async def search_bili_by_title(title: str) -> str:
    homepage_url = "https://www.bilibili.com"
    search_url = f"https://api.bilibili.com/x/web-interface/search/all/v2?keyword={urllib.parse.quote(title)}"

    async with aiohttp.ClientSession() as session:
        # set headers
        async with session.get(homepage_url) as resp:
            resp.raise_for_status()

        async with session.get(search_url) as resp:
            result = (await resp.json())["data"]["result"]

        # 只返回第一个结果
        return next(
            (i["data"][0]["arcurl"] for i in result if i["result_type"] == "video"), ""
        )


# 处理超过一万的数字
def handle_num(num: int) -> str:
    return f"{num / 10000:.2f}万" if num > 10000 else str(num)


async def video_detail(
    url: str,
    page: Optional[Match[str]] = None,
    time_location: Optional[Match[str]] = None,
) -> Tuple[Union[Message, str], str]:
    try:
        async with aiohttp.request("GET", url) as resp:
            res = (await resp.json()).get("data")
            if not res:
                return "解析到视频被删了/稿件不可见或审核中/权限不足", url
            vurl = f"https://www.bilibili.com/video/av{res['aid']}"
            title = f"标题：{res['title']}\n"
            cover = (
                MessageSegment.image(res["pic"])
                if config.analysis_display_image
                or "video" in config.analysis_display_image_list
                else ""
            )
            if page:
                page_str = page[0].replace("&amp;", "&")
                page_count = len(res["pages"])
                if page_count > 1 and (p := int(page_str[3:])) <= page_count:
                    vurl += f"?p={p}"
                    part = res["pages"][p - 1]["part"]
                    if part != res["title"]:
                        title += f"小标题：{part}\n"
            if time_location:
                time_str = time_location[0].replace("&amp;", "&")[3:]
                vurl += f"&t={time_str}" if page else f"?t={time_str}"
            pubdate = strftime("%Y-%m-%d %H:%M:%S", localtime(res["pubdate"]))
            tname = f"类型：{res['tname']} | UP：{res['owner']['name']} | 日期：{pubdate}\n"
            stat = f"播放：{handle_num(res['stat']['view'])} | 弹幕：{handle_num(res['stat']['danmaku'])} | 收藏：{handle_num(res['stat']['favorite'])}\n"
            stat += f"点赞：{handle_num(res['stat']['like'])} | 硬币：{handle_num(res['stat']['coin'])} | 评论：{handle_num(res['stat']['reply'])}\n"
            desc = f"简介：{res['desc']}"
            desc = "\n".join(i for i in desc.split("\n") if i)
            desc_list = desc.split("\n")
            if len(desc_list) > 4:
                desc = "\n".join(desc_list[:3]) + "……"
            msg = Message([title, cover, f"\n{vurl}\n", tname, stat, desc])  # type: ignore
            return msg, vurl
    except Exception as e:
        logger.exception("视频解析出错")
        return f"视频解析出错--Error: {type(e)}", ""


async def bangumi_detail(
    url: str, time_location: Optional[Match[str]]
) -> Tuple[Union[Message, str], str]:
    try:
        async with aiohttp.request("GET", url) as resp:
            res = (await resp.json()).get("result")
            if not res:
                return "", ""
            cover = (
                MessageSegment.image(res["cover"])
                if config.analysis_display_image
                or "bangumi" in config.analysis_display_image_list
                else ""
            )
            title = f"番剧：{res['title']}\n"
            desc = f"{res['newest_ep']['desc']}\n"
            index_title = ""
            style = "".join(f"{i}," for i in res["style"])
            style = f"类型：{style[:-1]}\n"
            evaluate = f"简介：{res['evaluate']}"
            if "season_id" in url:
                vurl = f"https://www.bilibili.com/bangumi/play/ss{res['season_id']}"
            elif "media_id" in url:
                vurl = f"https://www.bilibili.com/bangumi/media/md{res['media_id']}"
            else:
                epid = EPID_REGEX.search(url)[1]  # type: ignore
                for i in res["episodes"]:
                    if str(i["ep_id"]) == epid:
                        index_title = f"标题：{i['index_title']}\n"
                        break
                vurl = f"https://www.bilibili.com/bangumi/play/ep{epid}"
            if time_location:
                time_str = time_location[0].replace("&amp;", "&")[3:]
                vurl += f"?t={time_str}"
            msg = Message([title, cover, f"\n{vurl}\n", index_title, desc, style, evaluate])  # type: ignore
            return msg, vurl
    except Exception as e:
        logger.exception("番剧解析出错")
        return f"番剧解析出错--Error: {type(e)}", ""


async def live_detail(url: str) -> Tuple[Union[Message, str], str]:
    try:
        async with aiohttp.request("GET", url) as resp:
            res = await resp.json()
            if res["code"] != 0:
                return "", ""
            res = res["data"]
            uname = res["anchor_info"]["base_info"]["uname"]
            room_id = res["room_info"]["room_id"]
            title = res["room_info"]["title"]
            cover = (
                MessageSegment.image(res["room_info"]["cover"])
                if config.analysis_display_image
                or "live" in config.analysis_display_image_list
                else ""
            )
            live_status = res["room_info"]["live_status"]
            lock_status = res["room_info"]["lock_status"]
            parent_area_name = res["room_info"]["parent_area_name"]
            area_name = res["room_info"]["area_name"]
            online = res["room_info"]["online"]
            tags = res["room_info"]["tags"]
            watched_show = res["watched_show"]["text_large"]
            vurl = f"https://live.bilibili.com/{room_id}"
            if lock_status:
                lock_time = res["room_info"]["lock_time"]
                lock_time = strftime("%Y-%m-%d %H:%M:%S", localtime(lock_time))
                title = f"[已封禁]直播间封禁至：{lock_time}\n"
            elif live_status == 1:
                title = f"[直播中]标题：{title}\n"
            elif live_status == 2:
                title = f"[轮播中]标题：{title}\n"
            else:
                title = f"[未开播]标题：{title}\n"
            up = f"主播：{uname} 当前分区：{parent_area_name}-{area_name}\n"
            watch = f"观看：{watched_show} 直播时的人气上一次刷新值：{handle_num(online)}\n"
            if tags:
                tags = f"标签：{tags}\n"
            if live_status:
                player = f"独立播放器：https://www.bilibili.com/blackboard/live/live-activity-player.html?enterTheRoom=0&cid={room_id}"
            else:
                player = ""
            msg = Message([title, cover, f"\n{vurl}\n", up, watch, tags, player])  # type: ignore
            return msg, vurl
    except Exception as e:
        logger.exception("直播间解析出错")
        return f"直播间解析出错--Error: {type(e)}", ""


async def article_detail(url: str, cvid: str) -> Tuple[Union[Message, str], str]:
    try:
        async with aiohttp.request("GET", url) as resp:
            res = (await resp.json()).get("data")
            if not res:
                return "", ""
            images = (
                [MessageSegment.image(i) for i in res["origin_image_urls"]]
                if config.analysis_display_image
                or "article" in config.analysis_display_image_list
                else []
            )
            vurl = f"https://www.bilibili.com/read/cv{cvid}"
            title = f"标题：{res['title']}\n"
            up = f"作者：{res['author_name']} (https://space.bilibili.com/{res['mid']})\n"
            view = f"阅读数：{handle_num(res['stats']['view'])} "
            favorite = f"收藏数：{handle_num(res['stats']['favorite'])} "
            coin = f"硬币数：{handle_num(res['stats']['coin'])}"
            share = f"分享数：{handle_num(res['stats']['share'])} "
            like = f"点赞数：{handle_num(res['stats']['like'])} "
            dislike = f"不喜欢数：{handle_num(res['stats']['dislike'])}"
            desc = view + favorite + coin + "\n" + share + like + dislike
            msg = Message(title)
            if images:
                msg.extend(images)
                msg.append("\n")
            msg.extend([f"{vurl}\n", up, desc])  # type: ignore
            return msg, vurl
    except Exception as e:
        logger.exception("专栏解析出错")
        return f"专栏解析出错--Error: {type(e)}", ""


async def dynamic_detail(url: str) -> Tuple[Union[Message, str], str]:
    try:
        async with aiohttp.request("GET", url) as resp:
            res = (await resp.json())["data"].get("card")
            if not res:
                return "", ""
            card = json.loads(res["card"])
            dynamic_id = res["desc"]["dynamic_id"]
            vurl = f"https://t.bilibili.com/{dynamic_id}"
            item = card.get("item")
            if not item:
                return "动态不存在文字内容", vurl
            content = item.get("description") or item.get("content")
            content = content.replace("\r", "\n")
            if len(content) > 250:
                content = f"{content[:250]}......"
            images = (
                item.get("pictures", [])
                if config.analysis_display_image
                or "dynamic" in config.analysis_display_image_list
                else []
            )
            if images:
                images = [MessageSegment.image(i.get("img_src")) for i in images]
            elif pics := item.get("pictures_count"):
                content += f"\nPS：动态中包含{pics}张图片\n"
            if origin := card.get("origin"):
                if short_link := json.loads(origin).get("short_link"):
                    content += f"\n动态包含转发视频{short_link}\n"
                else:
                    content += "\n动态包含转发其他动态\n"
            msg = Message(content)
            if images:
                msg.extend(images)
                msg.append("\n")
            msg.append(f"{vurl}\n")
            return msg, vurl
    except Exception as e:
        logger.exception("动态解析出错")
        return f"动态解析出错--Error: {type(e)}", ""
