import asyncio
from nonebot import on_metaevent, on_command, get_bot, require
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import LifecycleMetaEvent
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .data_source import get_status


usage: str = """

发送 /status 查看Bot运行状态

""".strip()


__plugin_meta__ = PluginMetadata(
    name="状态",
    description="状态检查",
    usage=usage,
    type="application"
)


def check_first_connect(_: LifecycleMetaEvent) -> bool:
    return True

@on_metaevent(rule=check_first_connect, temp=True).handle()
async def _():
    if not scheduler.running:
        try:
            scheduler.start()
            logger.success("scheduler已启动.")
        except Exception as e:
            logger.error(f"scheduler启动失败!\n{repr(e)}")


ping = on_command("/ping", priority=1, block=True, permission=SUPERUSER)

@ping.handle()
async def _():
    await ping.finish("I'm fine.")


status = on_command("/status", priority=1, block=True, permission=SUPERUSER)

@status.handle()
async def _():
    msg, _ = await get_status()
    await status.finish(msg)


_status_lock = asyncio.Lock()

@scheduler.scheduled_job(
    "interval",
    id="状态检查",
    name="状态检查",
    minutes=30,
    misfire_grace_time=15
)
async def _() -> None:
    if _status_lock.locked():
        logger.warning("上一次状态检查尚未结束，跳过本次检查")
        return

    async with _status_lock:
        logger.info("检查资源消耗中...")

        msg, stat = await get_status()

        if not stat:
            logger.warning(msg)

            try:
                bot = get_bot()
            except Exception:
                bot = None

            if bot:
                try:
                    for superuser in bot.config.superusers:
                        await bot.send_private_msg(
                            user_id=int(superuser),
                            message=msg,
                        )
                except Exception as e:
                    logger.exception(e)
                    return
        else:
            logger.info("资源消耗正常")
