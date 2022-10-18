from nonebot import on_notice
from nonebot.adapters.onebot.v11 import (
    Bot, 
    GroupRecallNoticeEvent, 
    FriendRecallNoticeEvent, 
    MessageSegment, 
    Message,
)

from .utils import MessageChecker



recall_event = on_notice(priority=1, block=False)


@recall_event.handle()
async def _recall_group_event(bot: Bot, event: GroupRecallNoticeEvent):
    if event.is_tome():
        return
    try:
        repo = await bot.get_msg(message_id=event.message_id)
    except Exception:
        return
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
    msg = f"{user}@[群:{group}]\n撤回了\n{m}"
    for superuser in bot.config.superusers:
        await bot.send_private_msg(user_id=int(superuser), message=Message(msg))


@recall_event.handle()
async def _recall_private_event(bot: Bot, event: FriendRecallNoticeEvent):
    if event.is_tome():
        return
    try:
        repo = await bot.get_msg(message_id=event.message_id)
    except Exception:
        return
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
    msg = f"{user}@[私聊]撤回了\n{m}"
    for superuser in bot.config.superusers:
        await bot.send_private_msg(user_id=int(superuser), message=Message(msg))



def recall_msg_dealer(msg: dict) -> str:
    temp_m = list()
    for i in msg:
        _type = i.get("type", "idk")
        _data = i.get("data", "idk")
        if _type == "text":
            temp_m.append(_data["text"])
        elif _type == "image":
            url = _data["url"]
            check = MessageChecker(url).check_image_url
            if check:
                temp_m.append(MessageSegment.image(url))
            else:
                temp_m.append(f"[该图片可能包含非法内容，源url：{url}]")
        elif _type == "face":
            temp_m.append(MessageSegment.face(_data["id"]))
        else:
            temp_m.append(f"[{_data}]")
    repo = str().join(map(str, temp_m))
    return repo
