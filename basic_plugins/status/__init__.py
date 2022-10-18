from nonebot.plugin import on_command

from .data_source import Status

from nonebot.permission import SUPERUSER



ping = on_command("/ping", priority=1, block=True, permission=SUPERUSER)

@ping.handle()
async def _():
    await ping.finish(Status.ping())


status = on_command("/status", priority=1, block=True, permission=SUPERUSER)

@status.handle()
async def _():
    msg, _ = Status.get_status()
    await status.finish(msg)


info_msg = "桃桃世界第一可爱！"

