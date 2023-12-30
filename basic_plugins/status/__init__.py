from nonebot import on_metaevent, on_command, get_bot
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import LifecycleMetaEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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


scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


def check_first_connect(_: LifecycleMetaEvent) -> bool:
    return True

@on_metaevent(rule=check_first_connect, temp=True).handle()
async def _():
    if not scheduler.running:
        try:
            scheduler.start()
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


@scheduler.scheduled_job(
    "interval",
    id="状态检查",
    name="状态检查",
    minutes=30,
    misfire_grace_time=15
)
async def _():
    logger.info("检查资源消耗中...")
    msg, stat = await get_status()
    if not stat:
        logger.warning(msg)
        try:
            bot = get_bot()
        except Exception:
            bot = None
        try:
            if bot:
                for superuser in bot.config.superusers:
                    await bot.send_private_msg(user_id=int(superuser), message=msg)
        except Exception:
            return
    else:
        logger.info("资源消耗正常")
