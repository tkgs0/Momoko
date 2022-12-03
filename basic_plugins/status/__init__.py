from nonebot import on_command, require, logger, get_bot
from nonebot.permission import SUPERUSER

from .data_source import Status

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler


ping = on_command("/ping", priority=1, block=True, permission=SUPERUSER)

@ping.handle()
async def _():
    await ping.finish(Status.ping())


status = on_command("/status", priority=1, block=True, permission=SUPERUSER)

@status.handle()
async def _():
    msg, _ = Status.get_status()
    await status.finish(msg)


info_msg = "アトリは高性能ですから！"


@scheduler.scheduled_job('cron', minute='*/10', id='状态检查')
async def _():
    logger.info("开始检查资源消耗...")
    msg, stat = Status.get_status()
    if not stat:
        logger.warning(msg)

        bot = get_bot()
        for superuser in bot.config.superusers:
            await bot.send_private_msg(user_id=int(superuser), message=msg)
    else:
        logger.info("资源消耗正常")

