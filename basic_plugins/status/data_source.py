import os, time, psutil
from datetime import datetime
from typing import Tuple
from httpx import AsyncClient


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


async def get_status() -> Tuple[str, bool]:
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        inte_send = psutil.net_io_counters().bytes_sent / 1000000
        inte_recv = psutil.net_io_counters().bytes_recv / 1000000

        process = psutil.Process(os.getpid())
        b_cpu = process.cpu_percent(interval=1)
        b_mem = process.memory_percent(memtype="rss")

        now = time.time()
        boot = psutil.boot_time()
        b = process.create_time()
        boot_time = str(
            datetime.utcfromtimestamp(now).replace(microsecond=0)
            - datetime.utcfromtimestamp(boot).replace(microsecond=0)
        )
        bot_time = str(
            datetime.utcfromtimestamp(now).replace(microsecond=0)
            - datetime.utcfromtimestamp(b).replace(microsecond=0)
        )
    except Exception as e:
        return f"状态检查失败!\n{repr(e)}", False

    msg = "アトリは、高性能ですから！"
    if cpu > 90:
        msg = "咱感觉有些头晕..."
        is_ok = False
        if mem > 90:
            msg = "咱感觉有点头晕并且有点累..."
            is_ok = False
    elif mem > 90:
        msg = "咱感觉有点累..."
        is_ok = False
    elif disk > 90:
        msg = "咱感觉身体要被塞满了..."
        is_ok = False
    else:
        is_ok = True

    baidu_ = await get_url('https://www.baidu.com/')
    google_ = await get_url('https://www.google.com/')
        
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

headers = {
    'Referer': 'https://github.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

async def get_url(url):
    async with AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=10)
        await response.aclose()
        return response.status_code

