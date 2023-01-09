from nonebot import on_command
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent
)



def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False



cls_group = on_command(
    "查看所有群组", rule=to_me(), permission=SUPERUSER, priority=1, block=True
)

@cls_group.handle()
async def _(bot: Bot):
    gl = await bot.get_group_list()
    msg = ["{group_id} {group_name}".format_map(g) for g in gl]
    msg = "\n".join(msg)
    msg = f"bot:{bot.self_id}\n| 群号 | 群名 | 共{len(gl)}个群\n" + msg
    await cls_group.finish(msg)



cls_friend = on_command(
    "查看所有好友", rule=to_me(), permission=SUPERUSER, priority=1, block=True
)

@cls_friend.handle()
async def _(bot: Bot):
    gl = await bot.get_friend_list()
    msg = ["{user_id} {nickname}".format_map(g) for g in gl]
    msg = "\n".join(msg)
    msg = f"| QQ号 | 昵称 | 共{len(gl)}个好友\n" + msg
    await cls_friend.finish(msg)



group_user_list = on_command(
    "拉取群成员列表", rule=to_me(), permission=SUPERUSER, priority=1, block=True
)

@group_user_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_list = await bot.get_group_member_list(group_id=group_id)
    user_list = "\n".join(str(user["user_id"]) for user in user_list)
    await group_user_list.finish(user_list)
