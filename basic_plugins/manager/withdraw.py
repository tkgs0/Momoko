from nonebot import on_command, logger
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER,
    ActionFailed,
)


withdraw_msg = on_command(
    "撤回",
    priority=5,
    block=True,
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN
)

@withdraw_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if event.reply:
        try:
            await bot.delete_msg(message_id=event.reply.message_id)
            await bot.delete_msg(message_id=event.message_id)
        except ActionFailed as e:
            logger.warning(repr(e))

