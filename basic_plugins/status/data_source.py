import os
import time
import psutil
from datetime import datetime


_status_msg = """
> Status Overview

[CPU: {p_cpu}% of {b_cpu}]
[Memory: {p_mem}% of {b_mem}]
[Disk usage: {p_disk}%]

[Net sent: {inteSENT}MB]
[Net recv: {inteRECV}MB]

[Bot runtime: {bot_time}]
[Platform runtime: {boot_time}]
{msg}
""".strip()


class Status():

    @staticmethod
    def ping() -> str:
        return "I'm fine."

    @staticmethod
    def get_status() -> tuple:
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            inte_send = psutil.net_io_counters().bytes_sent / 1000000  # type: ignore
            inte_recv = psutil.net_io_counters().bytes_recv / 1000000  # type: ignore

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
        except:
            return "获取状态信息失败", False

        msg = "アトリは、高性能ですから！"
        if cpu > 90:  # type: ignore
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

        msg0 = _status_msg.format(
            p_cpu=cpu,
            p_mem=mem,
            p_disk=disk,
            b_cpu=f"{b_cpu}%",
            b_mem="%.1f%%" % b_mem,
            inteSENT=inte_send,
            inteRECV=inte_recv,
            bot_time=bot_time,
            boot_time=boot_time,
            msg=msg,
        )

        return msg0, is_ok

