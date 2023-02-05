import asyncio, logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collections import defaultdict
from nonebot.log import LoguruHandler


scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

aps_logger = logging.getLogger("apscheduler")
aps_logger.setLevel(30)
aps_logger.handlers.clear()
aps_logger.addHandler(LoguruHandler())


class Limiter:
    def __init__(self, max_count: int, down_time: float):
        """冷却设置

        Args:
            max_count (int): 最大次数
            down_time (float): 到达次数后的冷却时间
        """
        self.max_count = max_count
        self.down_time = down_time
        self.count = defaultdict(int)

    def check(self, key: str) -> bool:
        if self.count[key] >= self.max_count:
            loop = asyncio.get_running_loop()
            loop.call_later(self.down_time, self.reset)
            return False
        return True

    def increase(self, key: str, times: int = 1) -> None:
        self.count[key] += times

    def reset(self, key: str) -> None:
        self.count[key] = 0

    def get_times(self, key: str) -> int:
        return self.count[key]
