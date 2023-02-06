from nonebot import on_fullmatch, logger
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    ActionFailed,
)


withdraw_msg = on_fullmatch(
    "撤回",
    priority=5,
    block=True,
    permission=SUPERUSER
)

@withdraw_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if event.reply:
        try:
            await bot.delete_msg(message_id=event.reply.message_id)
            await bot.delete_msg(message_id=event.message_id)
        except ActionFailed as e:
            logger.warning(repr(e))

