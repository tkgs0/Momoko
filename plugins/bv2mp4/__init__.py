import asyncio
import os
import re
import shutil
import subprocess
import time

from httpx import AsyncClient
try:
        import ujson as json
except ModuleNotFoundError:
        import json
from pathlib import Path
from typing import List, Optional, Set, Tuple
from urllib.parse import parse_qs, unquote, urlparse

from nonebot import logger, on_message
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.permission import SUPERUSER
from nonebot.plugin import get_plugin_config, PluginMetadata

from .config import Config



usage= f'''

b2v:
    -o  开启/关闭
    -c  设置cookie
    -q  设置清晰度
    -s  设置文件尺寸上限
    -l  查看列表

'''.strip()


__plugin_meta__ = PluginMetadata(
    name="B链解析",
    description="将B站视频转换解析为 mp4",
    usage=usage,
    type="application",
    supported_adapters={"~onebot.v11"},
)

DATA_DIR: Path = Path() / "data" / "bv2mp4"
DATA_DIR.parent.mkdir(parents=True, exist_ok=True)


FFMPEG = get_plugin_config(Config).ffmpeg_path


BV_DIR = Path(get_plugin_config(Config).bv_dir)
BV_DIR.mkdir(parents=True, exist_ok=True)


STATE = DATA_DIR / 'settings.json'

bv_state: dict = (
    json.loads(STATE.read_text("utf-8"))
    if STATE.is_file()
    else {"user": [], "group": [], "cookies": {}}
)


def save_state() -> None:
    STATE.write_text(
        json.dumps(bv_state, indent=2, ensure_ascii=False), "utf-8")


_processing: Set[str] = set()




CMD_LIST = {"查看转换列表", "查看列表", "转换列表"}
CMD_ENABLE_RE = re.compile(r"^转换\s*(\d+)$", flags=re.IGNORECASE)
CMD_DISABLE_RE = re.compile(r"^停止转换\s*(\d+)$", flags=re.IGNORECASE)
CMD_SET_COOKIE_RE = re.compile(r"^设置B站COOKIE\s+(.+)$", flags=re.S)
CMD_CLEAR_COOKIE = {"清除B站COOKIE", "删除B站COOKIE"}
CMD_SET_HEIGHT_RE = re.compile(r"^设置清晰度\s*(\d+)$", flags=re.IGNORECASE)
CMD_SET_MAXSIZE_RE = re.compile(r"^设置最大大小\s*(\d+)\s*MB$", flags=re.IGNORECASE)
CMD_SHOW_PARAMS = {"查看参数", "参数", "设置"}

# 域名匹配
BILI_URL_RE = re.compile(
    r"(https?://(?:[\w-]+\.)?(?:bilibili\.com|b23\.tv)/[^\s\"'<>]+)",
    flags=re.IGNORECASE,
)

# =========================
# 初始化函数
# =========================


def _init_plugin():
    global DATA_DIR, STATE_PATH, DOWNLOAD_DIR, COOKIE_FILE_PATH
    global bili_super_admins, FFMPEG_DIR

    if DATA_DIR is not None:
        return

    # 读取插件配置
    plugin_config = get_plugin_config(Config)

    # 获取数据目录
    DATA_DIR = store.get_plugin_data_dir()
    STATE_PATH = DATA_DIR / "state.json"
    COOKIE_FILE_PATH = DATA_DIR / "bili_cookies.txt"
    DOWNLOAD_DIR = DATA_DIR / "downloads"
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    logger.info(f"bili2mp4: DATA_DIR={DATA_DIR} STATE_PATH={STATE_PATH}")

    _load_state()

    # 解析FFmpeg路径
    if plugin_config.ffmpeg_path:
        ffmpeg_dir = Path(plugin_config.ffmpeg_path)
        ffmpeg_exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        ffmpeg_bin = ffmpeg_dir / ffmpeg_exe
        if ffmpeg_bin.exists():
            FFMPEG_DIR = str(ffmpeg_dir)
            logger.info(f"bili2mp4: 使用配置中的ffmpeg目录: {FFMPEG_DIR}")
        else:
            logger.warning(
                f"bili2mp4: 配置的ffmpeg目录不存在或无{ffmpeg_exe}: {ffmpeg_bin}"
            )
            FFMPEG_DIR = None
    else:
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            FFMPEG_DIR = os.path.dirname(ffmpeg_path)
            logger.info(f"bili2mp4: 从PATH找到ffmpeg: {ffmpeg_path}")
        else:
            logger.info("bili2mp4: 未找到ffmpeg")
            FFMPEG_DIR = None

    logger.info(f"bili2mp4: 初始化完成，超管={bili_super_admins}")


# =========================
# 状态读写
# =========================


def _save_state():
    if not STATE_PATH:
        return
    data = {
        "enabled_groups": list(enabled_groups),
        "bilibili_cookie": bilibili_cookie,
        "max_height": max_height,
        "max_filesize_mb": max_filesize_mb,
    }
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_state():
    global enabled_groups, bilibili_cookie, max_height, max_filesize_mb

    if not STATE_PATH or not STATE_PATH.exists():
        return

    try:
        with STATE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        enabled_groups = set(map(int, data.get("enabled_groups", [])))
        bilibili_cookie = data.get("bilibili_cookie", "")
        max_height = int(data.get("max_height", 0))
        max_filesize_mb = int(data.get("max_filesize_mb", 0))
    except Exception as e:
        logger.warning(f"bili2mp4: 状态加载失败: {e}")


def _get_help_message() -> str:
    """获取帮助信息"""
    return (
        "【nonebot-plugin-bili2mp4 帮助】\n\n"
        "管理员私聊命令：\n"
        "• 转换 <群号> - 开启指定群的B站视频转换功能\n"
        "• 停止转换 <群号> - 停止指定群的B站视频转换功能\n"
        "• 设置B站COOKIE <cookie字符串> - 设置B站Cookie以获取更高清晰度\n"
        "• 清除B站COOKIE - 清除已设置的B站Cookie\n"
        "• 设置清晰度 <数字> - 设置视频清晰度限制（如 720/1080，0 代表不限制）\n"
        "• 设置最大大小 <数字>MB - 设置视频大小限制（0 代表不限制）\n"
        "• 查看参数 - 查看当前配置参数\n"
        "• 查看转换列表 - 查看已开启转换功能的群列表\n\n"
        "Cookie中至少需要包含SESSDATA、bili_jct、DedeUserID和buvid3/buvid4四个字段"
    )


def _find_urls_in_text(text: str) -> List[str]:
    urls = []
    for m in BILI_URL_RE.findall(text or ""):
        if m not in urls:
            urls.append(m)
    try:
        parsed = urlparse(text)
        if parsed and parsed.query:
            qs = parse_qs(parsed.query)
            for key in ("url", "qqdocurl", "jumpUrl", "webpageUrl"):
                for v in qs.get(key, []):
                    v = unquote(v)
                    for u in BILI_URL_RE.findall(v):
                        if u not in urls:
                            urls.append(u)
    except Exception:
        pass
    return urls


def _walk_strings(obj) -> List[str]:
    out: List[str] = []
    try:
        if isinstance(obj, dict):
            for v in obj.values():
                out.extend(_walk_strings(v))
        elif isinstance(obj, list):
            for it in obj:
                out.extend(_walk_strings(it))
        elif isinstance(obj, str):
            out.append(obj)
    except Exception:
        pass
    return out


def _extract_bili_urls_from_event(event: GroupMessageEvent) -> List[str]:
    urls: List[str] = []
    try:
        for seg in event.message:
            # 1) 纯文本
            if seg.type == "text":
                txt = seg.data.get("text", "")
                for u in _find_urls_in_text(txt):
                    if u not in urls:
                        urls.append(u)
            # 2) JSON 卡片
            elif seg.type == "json":
                raw = seg.data.get("data") or seg.data.get("content") or ""
                for u in _find_urls_in_text(raw):
                    if u not in urls:
                        urls.append(u)
                try:
                    obj = json.loads(raw)
                    for s in _walk_strings(obj):
                        for u in _find_urls_in_text(s):
                            if u not in urls:
                                urls.append(u)
                except Exception:
                    pass
            # 3) XML 卡片
            elif seg.type == "xml":
                raw = seg.data.get("data") or seg.data.get("content") or ""
                for u in _find_urls_in_text(raw):
                    if u not in urls:
                        urls.append(u)
            # 4) 分享卡片
            elif seg.type == "share":
                u = seg.data.get("url") or ""
                for u2 in _find_urls_in_text(u):
                    if u2 not in urls:
                        urls.append(u2)
            else:
                s = str(seg)
                for u in _find_urls_in_text(s):
                    if u not in urls:
                        urls.append(u)
    except Exception as e:
        logger.debug(f"bili2mp4: 提取链接异常: {e}")
    return urls


def _build_browser_like_headers() -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.bilibili.com/",
        "Origin": "https://www.bilibili.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
    }


def _expand_short_url(u: str, timeout: float = 8.0) -> str:
    try:
        host = urlparse(u).hostname or ""
        if host.lower() not in {"b23.tv", "www.b23.tv"}:
            return u
        hdrs = {
            "User-Agent": _build_browser_like_headers()["User-Agent"],
            "Referer": "https://www.bilibili.com/",
        }
        try:
            req = urllib.request.Request(u, headers=hdrs, method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                final = resp.geturl()
                return final or u
        except Exception:
            req = urllib.request.Request(u, headers=hdrs, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                final = resp.geturl()
                return final or u
    except Exception as e:
        logger.debug(f"bili2mp4: 短链展开失败，使用原链接（{u}）：{e}")
        return u


def _ensure_cookiefile(cookie_string: str) -> Optional[str]:
    """
    将 Cookie 字符串转为 Netscape 格式，供 yt-dlp 使用。
    """
    if COOKIE_FILE_PATH is None:
        return None

    cookie_string = (cookie_string or "").strip().strip(";")
    if not cookie_string:
        if COOKIE_FILE_PATH.exists():
            try:
                if COOKIE_FILE_PATH.exists():
                    COOKIE_FILE_PATH.unlink()
            except Exception:
                pass
        return None

    pairs = []
    for part in cookie_string.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k and v:
            pairs.append((k.strip(), v.strip()))

    if not pairs:
        return None

    expiry = int(time.time()) + 180 * 24 * 3600
    lines = [
        "# Netscape HTTP Cookie File",
        "# Generated by nonebot_plugin_bili2mp4",
        "",
    ]

    for k, v in pairs:
        # domain include_subdomains path secure expiry name value
        lines.append(f".bilibili.com\tTRUE\t/\tFALSE\t{expiry}\t{k}\t{v}")

    try:
        with COOKIE_FILE_PATH.open("w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        logger.info("bili2mp4: Cookie 已设置")
        return str(COOKIE_FILE_PATH)
    except Exception:
        return None


def _check_video_file(path: str) -> bool:
    """检查视频文件大小和分辨率"""
    try:
        # 检查文件大小
        path_obj = Path(path)
        if max_filesize_mb and path_obj.exists():
            size_mb = path_obj.stat().st_size / (1024 * 1024)
            if size_mb > max_filesize_mb:
                if path_obj.exists():
                    path_obj.unlink()
                return False

        # 检查视频分辨率
        if path_obj.exists():
            ffprobe_exe = "ffprobe.exe" if os.name == "nt" else "ffprobe"
            cmd = [ffprobe_exe]
            if FFMPEG_DIR:
                cmd[0] = str(Path(FFMPEG_DIR) / ffprobe_exe)

            cmd.extend(
                [
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height",
                    "-of",
                    "csv=p=0",
                    path,
                ]
            )

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                try:
                    width, height = result.stdout.strip().split(",")
                    # 检查是否设置了高度限制
                    if max_height and int(height) > max_height:
                        path_obj.unlink()
                        return False
                except ValueError:
                    pass
        return True
    except Exception:
        return False


async def _send_video_with_timeout(
    bot: Bot, group_id: int, path: str, title: str
) -> None:
    """发送视频，带超时处理"""
    sent = False
    try:
        await bot.send_group_msg(
            group_id=group_id,
            message=MessageSegment.video(file=path)
            + Message(f"\n{title or 'B站视频'}"),
        )
        logger.info(f"bili2mp4: 视频已发送到群 {group_id}: {title or 'B站视频'}")
        sent = True
    except Exception as e:
        error_msg = str(e)
        if not ("timeout" in error_msg.lower() and "websocket" in error_msg.lower()):
            logger.warning(
                f"bili2mp4: 发送视频失败: {Path(path).name} | group={group_id} | err={e}"
            )
    finally:
        if sent:
            try:
                path_obj = Path(path)
                if path_obj.exists():
                    path_obj.unlink()
            except Exception as e:
                logger.debug(f"Failed to delete temp file {path}: {e}")


def _build_format_candidates(height_limit: int, size_limit_mb: int) -> List[str]:
    """构建格式候选列表"""
    h = height_limit if height_limit and height_limit > 0 else None

    if not h:
        return ["bv*+ba/best"]

    # 根据清晰度限制构建格式候选
    format_map = {
        1080: [
            f"bv*[height>=1080]+ba/best",
            f"bv*[height>=720]+ba/best",
            "bv*+ba/best",
        ],
        720: [f"bv*[height>=720]+ba/best", f"bv*[height>=480]+ba/best", "bv*+ba/best"],
        480: [f"bv*[height>=480]+ba/best", "bv*+ba/best"],
    }

    # 根据高度选择最适合的格式列表
    for threshold, formats in sorted(format_map.items(), reverse=True):
        if h >= threshold:
            return formats

    # 默认格式
    return ["bv*+ba/best"]

def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and ("avc" in f['vcodec'] or "hvc" in f['vcodec']) and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }

def _download_with_ytdlp(
    url: str, cookie: str, out_dir, height_limit: int, size_limit_mb: int
) -> Tuple[str, str]:
    try:
        from yt_dlp import YoutubeDL  # type: ignore
        from yt_dlp.utils import DownloadError  # type: ignore
    except Exception:
        raise ImportError("yt_dlp not installed")

    from pathlib import Path

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    final_url = _expand_short_url(url)

    # 构建 Cookie 文件
    cookiefile = _ensure_cookiefile(cookie)
    candidates = _build_format_candidates(height_limit, size_limit_mb)
    last_err: Optional[Exception] = None

    for i, fmt in enumerate(candidates):
        headers = _build_browser_like_headers()
        ydl_opts = {
            "format": format_selector,
            "outtmpl": str(out_dir / "%(title).80s [%(id)s].%(ext)s"),
            "noplaylist": True,
            "merge_output_format": "mp4",
            "quiet": False,
            "no_warnings": False,
            "max_filesize" : size_limit_mb*1024*1024,  # MB in bytes
            "http_headers": headers,
            "extractor_args": {
                "bili": {
                    "player_client": ["android", "web"],
                    "lang": ["zh-CN"],
                }
            },
        }

        if FFMPEG_DIR:
            ydl_opts["ffmpeg_location"] = FFMPEG_DIR

        # 设置 Cookie
        if cookiefile:
            ydl_opts["cookiefile"] = cookiefile
            logger.info(f"bili2mp4: 使用 cookiefile: {cookiefile}")
        elif cookie:
            headers["Cookie"] = cookie
            logger.info("bili2mp4: 使用 Cookie header")

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(final_url, download=True)
                title = info.get("title") or "B站视频"

                # 获取下载信息
                height = info.get("height", 0)
                logger.info(f"bili2mp4: 下载完成: {title} ({height}p)")

                # 定位文件
                final_path = _locate_final_file(ydl, info)
                if not final_path or not Path(final_path).exists():
                    raise RuntimeError("未找到已下载的视频文件，可能未安装 ffmpeg")
                return final_path, title
        except DownloadError as e:
            last_err = e
            continue
        except Exception as e:
            last_err = e
            continue

    if last_err:
        raise RuntimeError(str(last_err))
    raise RuntimeError("无法下载该视频")


def _locate_final_file(ydl, info) -> Optional[str]:
    for key in ("requested_downloads", "requested_formats"):
        arr = info.get(key)
        if isinstance(arr, list):
            for it in arr:
                fp = it.get("filepath")
                if fp and os.path.exists(fp):
                    return fp
    for key in ("filepath", "_filename"):
        fp = info.get(key)
        if fp and os.path.exists(fp):
            return fp
    # 预测合并后 mp4
    base = ydl.prepare_filename(info)
    root, _ = os.path.splitext(base)
    candidate = root + ".mp4"
    if os.path.exists(candidate):
        return candidate
    # 兜底：按视频ID在目录中搜
    vid = info.get("id") or ""
    if vid:
        dirpath = os.path.dirname(base) or os.getcwd()
        try:
            files = [dirpath / f for f in os.listdir(dirpath) if vid in f]
            if files:
                files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                return str(files[0])
        except Exception:
            pass
    return None


async def _download_and_send(bot: Bot, group_id: int, url: str) -> None:
    # 执行下载
    try:
        path, title = await asyncio.to_thread(
            _download_with_ytdlp,
            url,
            bilibili_cookie,
            DOWNLOAD_DIR,  # 修复：传递Path对象而不是字符串
            max_height,
            max_filesize_mb,
        )
    except (ImportError, RuntimeError) as e:
        logger.warning(f"下载环境异常: {e}")
        return
    except Exception as e:
        logger.error(f"bili2mp4: 下载异常: {e}")
        return

    # 检查文件大小和分辨率
    if not _check_video_file(path):
        return

    # 发送视频
    await _send_video_with_timeout(bot, group_id, path, title)


async def _handle_group_command(
    bot: Bot, event: PrivateMessageEvent, text: str
) -> bool:
    """处理群相关命令"""
    global enabled_groups

    # 开启群
    m = CMD_ENABLE_RE.fullmatch(text)
    if m:
        gid = int(m.group(1))
        if gid in enabled_groups:
            await bot.send(event, Message(f"ℹ️ 群 {gid} 已开启转换"))
        else:
            enabled_groups.add(gid)
            _save_state()
            await bot.send(event, Message(f"✅ 已开启群 {gid} 的B站视频转换"))
        return True

    # 关闭群
    m = CMD_DISABLE_RE.fullmatch(text)
    if m:
        gid = int(m.group(1))
        if gid in enabled_groups:
            enabled_groups.discard(gid)
            _save_state()
            await bot.send(event, Message(f"🛑 已停止群 {gid} 的B站视频转换"))
        else:
            await bot.send(event, Message(f"ℹ️ 群 {gid} 未开启转换"))
        return True

    # 查看列表
    if text in CMD_LIST:
        if enabled_groups:
            sorted_g = sorted(list(enabled_groups))
            await bot.send(
                event, Message("当前已开启转换的群：" + ", ".join(map(str, sorted_g)))
            )
        else:
            await bot.send(event, Message("暂无开启转换的群"))
        return True

    return False


async def _handle_config_command(
    bot: Bot, event: PrivateMessageEvent, text: str
) -> bool:
    """处理配置相关命令"""
    global bilibili_cookie, max_height, max_filesize_mb

    # 设置Cookie
    m = CMD_SET_COOKIE_RE.fullmatch(text)
    if m:
        bilibili_cookie = m.group(1).strip()
        _save_state()
        await bot.send(event, Message("✅ 已设置B站 Cookie"))
        return True

    # 清除Cookie
    if text in CMD_CLEAR_COOKIE:
        bilibili_cookie = ""
        _save_state()
        await bot.send(event, Message("🧹 已清除B站 Cookie"))
        return True

    # 设置清晰度
    m = CMD_SET_HEIGHT_RE.fullmatch(text)
    if m:
        h = int(m.group(1))
        if h < 0:
            h = 0
        max_height = h
        _save_state()
        await bot.send(
            event, Message(f"⏱ 清晰度已设置为 {'不限制' if h == 0 else f'<= {h}p'}")
        )
        return True

    # 设置最大大小（MB）
    m = CMD_SET_MAXSIZE_RE.fullmatch(text)
    if m:
        lim = int(m.group(1))
        if lim < 0:
            lim = 0
        max_filesize_mb = lim
        _save_state()
        await bot.send(
            event,
            Message(f"📦 文件大小限制为 {'不限制' if lim == 0 else f'<= {lim}MB'}"),
        )
        return True

    # 查看参数
    if text in CMD_SHOW_PARAMS:
        await bot.send(
            event,
            Message(
                f"参数：清晰度<= {max_height or '不限'}；大小<= {str(max_filesize_mb) + 'MB' if max_filesize_mb else '不限'}；"
                f"Cookie={'已设置' if bool(bilibili_cookie) else '未设置'}；启用群数={len(enabled_groups)}"
            ),
        )
        return True

    return False


# =========================
# 事件监听
# =========================

# 群消息监听
group_listener = on_message(priority=100, block=False)


@group_listener.handle()
async def handle_group(bot: Bot, event: GroupMessageEvent):
    try:
        _init_plugin()

        group_id = int(event.group_id)
        if group_id not in enabled_groups:
            return

        urls = _extract_bili_urls_from_event(event)
        if not urls:
            logger.debug(f"bili2mp4: 群{group_id} 未在该消息中发现B站链接")
            return

        url = urls[0]
        key = f"{group_id}|{url}"
        if key in _processing:
            logger.debug(f"bili2mp4: 已在处理中，忽略重复: {key}")
            return
        _processing.add(key)
        logger.info(f"bili2mp4: 检测到B站链接")

        async def work():
            try:
                await _download_and_send(bot, group_id, url)
            except Exception as e:
                logger.warning(f"bili2mp4: 处理失败: {e}")
            finally:
                _processing.discard(key)

        asyncio.create_task(work())
    except Exception as e:
        logger.warning(f"bili2mp4: 群消息处理异常: {e}")


# 私聊控制
ctrl_listener = on_message(priority=50, permission=SUPERUSER, block=False)


@ctrl_listener.handle()
async def handle_private(bot: Bot, event: PrivateMessageEvent):
    _init_plugin()

    try:
        uid = int(event.user_id)
    except Exception:
        return
    if uid not in bili_super_admins:
        return

    text = (event.get_message() or Message()).extract_plain_text().strip()
    if not text:
        return

    try:
        # 帮助
        if text == "fhelp":
            await bot.send(event, Message(_get_help_message()))
            return

        if await _handle_group_command(bot, event, text):
            return

        if await _handle_config_command(bot, event, text):
            return
    except Exception as e:
        logger.warning(f"bili2mp4: 处理管理员命令失败: {e}")

    return
