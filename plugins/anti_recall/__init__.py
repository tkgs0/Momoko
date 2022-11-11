from nonebot import on_notice, logger
from nonebot.adapters.onebot.v11 import (
    Bot, 
    GroupRecallNoticeEvent, 
    FriendRecallNoticeEvent, 
    Message,
)

from .utils import recall_msg_dealer, MessageChecker



recall_event = on_notice(priority=1, block=False)


@recall_event.handle()
async def _(bot: Bot, event: FriendRecallNoticeEvent):
    if event.is_tome():
        return

    try:
        repo = await bot.get_msg(message_id=event.message_id)
    except Exception:
        return

    logger.debug(f"Recall raw msg:\n{repo}")
    user = event.user_id
    repo = repo["message"]

    try:
        m = recall_msg_dealer(repo)
    except Exception:
        check = MessageChecker(repo).check_cq_code
        if not check:
            m = repo
        else:
            return
    msg = f"{user}@[私聊]\n撤回了\n{m}"
    for superuser in bot.config.superusers:
        await bot.send_private_msg(user_id=int(superuser), message=Message(msg))


@recall_event.handle()
async def _(bot: Bot, event: GroupRecallNoticeEvent):
    if event.is_tome():
        return

    try:
        repo = await bot.get_msg(message_id=event.message_id)
    except Exception:
        return

    logger.debug(f"Recall raw msg:\n{repo}")
    user = event.user_id
    group = event.group_id
    repo = repo["message"]

    try:
        m = recall_msg_dealer(repo)
    except Exception:
        check = MessageChecker(repo).check_cq_code
        if not check:
            m = repo
        else:
            return
    msg = f"{user}@[群聊:{group}]\n撤回了\n{m}"
    for superuser in bot.config.superusers:
        await bot.send_private_msg(user_id=int(superuser), message=Message(msg))
