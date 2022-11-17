from nonebot import logger, on_command
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
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



del_group = on_command("退群", rule=to_me(), permission=SUPERUSER, priority=1, block=True)

@del_group.handle()
async def _(event: MessageEvent, bot: Bot, arg: Message = CommandArg()):
    gids = arg.extract_plain_text().strip().split()
    if gids:
        for gid in gids:
            if not is_number(gid):
                await del_group.finish(f"群号必须为数字", at_sender=True)
        msg = ''
        for gid in gids:
            try:
                await bot.set_group_leave(group_id=int(gid))
                logger.info(f"退出群聊 {gid} 成功")
                msg += f"\n退出群聊 {gid} 成功"
            except Exception as e:
                logger.info(f"退出群聊 {gid} 失败 e:{e}")
                msg += f"\n退出群聊 {gid} 失败 e:{e}"
        await del_group.finish(msg, at_sender=True)

    elif isinstance(event, GroupMessageEvent):
        group_id = event.group_id
        try:
            await bot.set_group_leave(group_id=group_id)
            logger.info(f"退出群聊 {group_id} 成功")
            await bot.send_private_msg(user_id=event.user_id, message=f"退出群聊 {group_id} 成功")
        except Exception as e:
            logger.info(f"退出群聊 {group_id} 失败 e:{e}")
            await del_group.finish(f"退出群聊失败 e:{e}", at_sender=True)

    else:
        await del_group.finish(f"需要群号", at_sender=True)



group_user_list = on_command(
    "拉取群成员列表", rule=to_me(), permission=SUPERUSER, priority=1, block=True
)

@group_user_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_list = await bot.get_group_member_list(group_id=group_id)
    user_list = "\n".join(str(user["user_id"]) for user in user_list)
    await group_user_list.finish(user_list)
