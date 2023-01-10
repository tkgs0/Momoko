import re, asyncio, random
from nonebot import on_command, on_notice
from nonebot.log import logger
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
    # GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent,
    GROUP_ADMIN,
    GROUP_OWNER
)


ban = on_command(
    "禁言",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)

unban = on_command(
    "解除禁言",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


selfban = on_command(
    "我要自闭",
    aliases={'来份先辈特调红茶', '来杯先辈特调红茶'},
    priority=5,
    block=True
)


wholeban = on_command(
    "开启全员禁言",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


unwholeban = on_command(
    "关闭全员禁言",
    aliases={'解除全员禁言'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


setadmin = on_command(
    "设为管理",
    aliases={'升为管理'},
    permission=SUPERUSER | GROUP_OWNER,
    priority=1,
    block=True
)


unsetadmin = on_command(
    "撤销管理",
    aliases={'取消管理'},
    permission=SUPERUSER | GROUP_OWNER,
    priority=1,
    block=True
)


setgroupcard = on_command(
    "修改名片",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


specialtitle = on_command(
    "设置头衔",
    aliases={'修改头衔'},
    permission=SUPERUSER | GROUP_OWNER,
    priority=1,
    block=True
)


applyspecialtitle = on_command(
    "申请头衔",
    priority=5,
    block=True
)


kick = on_command(
    "踢出群聊",
    aliases={'移出群聊', '踢出本群', '移出本群'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


del_group = on_command(
    "退群",
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)


@ban.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    _time = ban_time(arg)
    msg = await ban_user(bot, event.group_id, uids,
        _time if _time <= 30*24*60*60-60 else 30*24*60*60-60)
    await ban.finish(msg)


@unban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    msg = await ban_user(bot, event.group_id, uids, 0)
    await unban.finish(msg)


@selfban.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    uids = [event.user_id,]
    _time = ban_time(arg)
    msg = await ban_user(bot, event.group_id, uids,
        _time if _time <= 30*24*60*60-60 else 30*24*60*60-60)
    await selfban.finish('咕噜咕噜~' if msg else None)


@wholeban.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = await setwholeban(True, bot, event, arg)
    await wholeban.finish(msg if msg != True else '天黑请闭眼~')


@unwholeban.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = await setwholeban(False, bot, event, arg)
    await wholeban.finish(msg if msg != True else '天亮请睁眼~')


@setadmin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    x = True
    try:
        for uid in uids:
            await bot.set_group_admin(
                group_id=event.group_id, user_id=uid, enable=True)
    except Exception as e:
        logger.warning(repr(e))
        x = None
    await setadmin.finish(x if not x else '设置成功~')


@unsetadmin.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    x = True
    try:
        for uid in uids:
            await bot.set_group_admin(
                group_id=event.group_id, user_id=uid, enable=False)
    except Exception as e:
        logger.warning(repr(e))
        x = None
    await unsetadmin.finish(x if not x else '设置成功~')


@setgroupcard.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    content = arg.extract_plain_text().strip()
    x = True
    try:
        for uid in uids:
            await bot.set_group_card(
                group_id=event.group_id,
                user_id=uid,
                card=content
            )
    except Exception as e:
        logger.warning(repr(e))
        x = None
    await setgroupcard.finish(x if not x else '嗯, 很棒的名字呢~')


@specialtitle.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    content = arg.extract_plain_text().strip()
    x = True
    try:
        for uid in uids:
            await bot.set_group_special_title(
                group_id=event.group_id,
                user_id=uid,
                special_title=content,
                duration=-1
            )
    except Exception as e:
        logger.warning(repr(e))
        x = None
    await specialtitle.finish(x if not x else '嗯, 很棒的头衔呢~')


@applyspecialtitle.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    content = arg.extract_plain_text().strip()
    x = True
    try:
        await bot.set_group_special_title(
            group_id=event.group_id,
            user_id=event.user_id,
            special_title=content,
            duration=-1
        )
    except Exception as e:
        logger.warning(repr(e))
        x = None
    await specialtitle.finish(x if not x else '嗯, 很棒的头衔呢~')


@kick.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    try:
        for uid in uids:
            await bot.set_group_kick(
                group_id=event.group_id,
                user_id=uid,
                reject_add_request=False
            )
    except Exception as e:
        logger.warning(repr(e))


@del_group.handle()
async def _(event: MessageEvent, bot: Bot, arg: Message = CommandArg()):
    gids = arg.extract_plain_text().strip().split()
    if gids:
        for gid in gids:
            if not is_number(gid):
                await del_group.finish("群号必须为数字", at_sender=True)
        msg = ''
        for gid in gids:
            try:
                await bot.set_group_leave(group_id=int(gid))
                logger.info(f"退出群聊 {gid} 成功")
                msg += f"\n退出群聊 {gid} 成功"
            except Exception as e:
                logger.warning(f"退出群聊 {gid} 失败\n{repr(e)}")
                msg += f"\n退出群聊 {gid} 失败 {e.__class__.__name__}"
        await del_group.send('', at_sender=True)
        await del_group.finish(msg.lstrip())

    elif isinstance(event, GroupMessageEvent):
        group_id = event.group_id
        msg = ''
        try:
            await bot.set_group_leave(group_id=group_id)
            logger.info(f"退出群聊 {group_id} 成功")
            msg += f"退出群聊 {group_id} 成功"
        except Exception as e:
            logger.warning(f"退出群聊 {group_id} 失败\n{repr(e)}")
            msg += f"退出群聊 {group_id} 失败\n{repr(e)}"
        await bot.send_private_msg(user_id=event.user_id, message=msg)

    else:
        await del_group.finish(f"需要群号", at_sender=True)


async def ban_user(bot: Bot, gid: int, userlist: list, _time: int):
    if not userlist:
        logger.warning('未指定要禁言的用户!')
        return None
    x = True
    try:
        for user in userlist:
            await bot.set_group_ban(user_id=user, group_id=gid, duration=_time)
    except Exception as e:
        logger.warning(repr(e))
        x = None
    return x if not x else '设置成功~'


def ban_time(arg: Message = CommandArg()) -> int:
    try:
        _time = arg.extract_plain_text().strip()
        _time = re.search('[1-9]\d*(天|小?(时|時)|分|)', _time).group()  # type: ignore
        time1 = re.match('\d*', _time).group()  # type: ignore
        time2 = _time.replace(time1, '')
        time1 = int(time1)
        if '时' in time2 or '時' in time2:
            return time1*60*60
        if '天' in time2:
            return time1*60*60*24
        return time1*60
    except:
        return 43200


async def setwholeban(
    enable: bool,
    bot: Bot,
    event: MessageEvent,
    arg: Message = CommandArg(),
):
    gids = arg.extract_plain_text().strip().split()
    if not gids:
        if isinstance(event, GroupMessageEvent):
            gids.append(f'{event.group_id}')
        else:
            return '用法: \n开启(关闭)全员禁言 群 群1 群2 ...'
    for gid in gids:
        if not is_number(gid):
            return '参数错误, 群号必须是数字..'
    x = True
    try:
        for gid in gids:
            await bot.set_group_whole_ban(group_id=int(gid), enable=enable)
    except Exception as e:
        logger.warning(repr(e))
        x = None
    return x if not x else True
    

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



group_member_event = on_notice(priority=1)

# @group_member_event.handle()
# async def _(event: GroupIncreaseNoticeEvent):
#     await asyncio.sleep(random.random()*2+1)
#     await group_member_event.finish('欢迎~')

@group_member_event.handle()
async def _(event: GroupDecreaseNoticeEvent):
    await asyncio.sleep(random.random()*2+1)
    await group_member_event.finish(f'一位不愿透露姓名的网友({event.user_id})离开了我们...')
