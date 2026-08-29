import asyncio, os, psutil, time
from datetime import timedelta
from typing import Tuple

from httpx import AsyncClient
from nonebot.log import logger


_STATUS_MSG = """
> Status Overview

[CPU: {b_cpu}% of {p_cpu}%]
[Memory: {b_mem} of {p_mem}%]
[Disk usage: {p_disk}%]

[Baidu: {baidu_}]
[Google: {google_}]

[Net sent: {inteSENT}MB]
[Net recv: {inteRECV}MB]

[Run Duration]
[Bot: {bot_time}]
[Platform: {boot_time}]
{msg}
""".strip()


headers = {
    "Referer": "https://github.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}


async def get_url(client: AsyncClient, url: str):
    try:
        response = await client.get(
            url,
            headers=headers,
            timeout=10,
        )
        return response.status_code
    except Exception as e:
        logger.warning(repr(e))
        return e.__class__.__name__


async def get_status() -> Tuple[str, bool]:
    try:
        # psutil 的同步 API，避免 interval=1 阻塞 event loop
        cpu = psutil.cpu_percent(interval=None)

        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        net = psutil.net_io_counters()
        inte_send = net.bytes_sent / 1_000_000
        inte_recv = net.bytes_recv / 1_000_000

        process = psutil.Process(os.getpid())

        b_cpu = process.cpu_percent(interval=None)
        b_mem = process.memory_percent(memtype="rss")

        now = time.time()
        boot = psutil.boot_time()
        created = process.create_time()

        boot_time = str(timedelta(seconds=int(now - boot)))
        bot_time = str(timedelta(seconds=int(now - created)))

    except Exception as e:
        return f"状态检查失败!\n{repr(e)}", False

    msg = "アトリは、高性能ですから！"
    is_ok = True

    if cpu > 90:
        msg = "咱感觉有些头晕..."
        is_ok = False

        if mem > 90:
            msg = "咱感觉有点头晕并且有点累..."

    elif mem > 90:
        msg = "咱感觉有点累..."
        is_ok = False

    elif disk > 90:
        msg = "咱感觉身体要被塞满了..."
        is_ok = False

    async with AsyncClient() as client:
        baidu_, google_ = await asyncio.gather(
            get_url(client, "https://www.baidu.com/"),
            get_url(client, "https://www.google.com/"),
        )

    msg0 = _STATUS_MSG.format(
        p_cpu=cpu,
        p_mem=mem,
        p_disk=disk,
        b_cpu=b_cpu,
        b_mem="%.1f%%" % b_mem,
        baidu_=baidu_,
        google_=google_,
        inteSENT=inte_send,
        inteRECV=inte_recv,
        bot_time=bot_time,
        boot_time=boot_time,
        msg=msg,
    )

    return msg0, is_ok
