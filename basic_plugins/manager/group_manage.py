import time
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from nonebot import on_command, on_message, logger
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER,
    unescape,
    ActionFailed,
)
from nonebot.adapters.onebot.v11.helpers import (
    Cooldown,
    extract_image_urls,
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

from .utils import (
    flmt_notice,
    err_info,
    is_number,
    ban_user,
    ban_time,
    setwholeban,
)


nmlist = Path() / 'data' / 'group_manage' / 'nmlist.json'
nmlist.parent.mkdir(parents=True, exist_ok=True)
anonymous = (
    json.loads(nmlist.read_text('utf-8'))
    if nmlist.is_file()
    else {}
)


def save_nmlist() -> None:
    nmlist.write_text(json.dumps(anonymous), encoding='utf-8')


@on_message(priority=2, block=False).handle()
async def _(event: GroupMessageEvent):
    if nm := event.anonymous:
        anonymous.update({
            event.message_id: {
                'time': time.time(),
                'flag': nm.flag
            }
        })
        save_nmlist()
    return


@scheduler.scheduled_job(
    'interval',
    id='过期会话清理',
    name='过期会话清理',
    minutes=30,
    misfire_grace_time=15
)
async def _():
    logger.debug('清理过期的会话记录...')
    for i in anonymous:
        if time.time() - i['time'] > 60*60*24*3:
            anonymous.pop(i)
            save_nmlist()


kick = on_command(
    '踢出群聊',
    aliases={'移出群聊', '踢出本群', '移出本群'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@kick.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    try:
        for uid in uids:
            await bot.set_group_kick(
                group_id=event.group_id,
                user_id=uid,
                reject_add_request=False
            )
    except ActionFailed as e:
        logger.warning(err_info(e))


async def is_reply(bot: Bot, event: MessageEvent) -> str | int | None:
    if event.reply:
        msg_id = event.reply.message_id
        if msg_id in anonymous:
            flag = anonymous[msg_id]['flag']
            return flag
        
        try:
            msg = await bot.get_msg(message_id=msg_id)
            uid = msg['sender']['user_id']
        except ActionFailed as e:
            logger.warning(err_info(e))
            uid = None
        except:
            uid = None
        return uid
    return None


ban = on_command(
    '禁言',
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@ban.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    _time = ban_time(arg)
    flag = await is_reply(bot, event) if not uids else None
    if isinstance(flag, int):
        uids.append(flag)
        flag = None
    msg = await ban_user(bot, event.group_id, uids, _time, flag)
    await ban.finish(msg)


unban = on_command(
    '解除禁言',
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@unban.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    flag = await is_reply(bot, event) if not uids else None
    if isinstance(flag, int):
        uids.append(flag)
        flag = None
    msg = await ban_user(bot, event.group_id, uids, 0, flag)
    await unban.finish(msg)


selfban = on_command(
    '我要自闭',
    aliases={'来份先辈特调红茶', '来杯先辈特调红茶'},
    priority=5,
    block=True
)


@selfban.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    uids = [event.user_id,]
    flag = await is_reply(bot, event) if not uids else None
    if isinstance(flag, int):
        uids.append(flag)
        flag = None
    _time = ban_time(arg)
    msg = await ban_user(bot, event.group_id, uids, _time, flag)
    await selfban.finish('咕噜咕噜~' if msg else None)


wholeban = on_command(
    '开启全员禁言',
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@wholeban.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = await setwholeban(True, bot, event, arg)
    await wholeban.finish(msg if msg != True else '天黑请闭眼~')


unwholeban = on_command(
    '关闭全员禁言',
    aliases={'解除全员禁言'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@unwholeban.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    msg = await setwholeban(False, bot, event, arg)
    await wholeban.finish(msg if msg != True else '天亮请睁眼~')

setadmin = on_command(
    '设为管理',
    aliases={'升为管理'},
    permission=SUPERUSER | GROUP_OWNER,
    priority=1,
    block=True
)


@setadmin.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    if not uids:
        logger.warning('未指定要设为管理的对象!')
        return
    x = True
    try:
        for uid in uids:
            await bot.set_group_admin(
                group_id=event.group_id, user_id=uid, enable=True)
    except ActionFailed as e:
        logger.warning(err_info(e))
        x = None
    await setadmin.finish(x if not x else '设置成功~')


unsetadmin = on_command(
    '撤销管理',
    aliases={'取消管理'},
    permission=SUPERUSER | GROUP_OWNER,
    priority=1,
    block=True
)


@unsetadmin.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    if not uids:
        logger.warning('未指定要取消管理的对象!')
        return
    x = True
    try:
        for uid in uids:
            await bot.set_group_admin(
                group_id=event.group_id, user_id=uid, enable=False)
    except ActionFailed as e:
        logger.warning(err_info(e))
        x = None
    await unsetadmin.finish(x if not x else '设置成功~')


setnm = on_command(
    '允许匿名', 
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@setnm.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        await bot.set_group_anonymous(group_id=event.group_id, enable=True)
    except ActionFailed as e:
        logger.warning(err_info(e))


unsetnm = on_command(
    '禁止匿名', 
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@unsetnm.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        await bot.set_group_anonymous(group_id=event.group_id, enable=True)
    except ActionFailed as e:
        logger.warning(err_info(e))


setgroupcard = on_command(
    '修改名片',
    aliases={'修改备注'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@setgroupcard.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    if not uids:
        logger.warning('未指定要修改备注的对象!')
        return
    content = unescape(arg.extract_plain_text().strip())
    if len(bytes(content, encoding='utf-8')) > 60:
        await setgroupcard.finish('名字太长啦!')
    x = True
    try:
        for uid in uids:
            await bot.set_group_card(
                group_id=event.group_id,
                user_id=uid,
                card=content
            )
    except ActionFailed as e:
        logger.warning(err_info(e))
        x = None
    await setgroupcard.finish(x if not x else '嗯, 很棒的名字呢~')


setgroupname = on_command(
    '设置群名',
    aliases={'修改群名'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=1,
    block=True
)


@setgroupname.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    content = unescape(arg.extract_plain_text().strip())
    try:
        await bot.set_group_name(group_id=event.group_id, group_name=content)
    except ActionFailed as e:
        logger.warning(err_info(e))
        return
    await setgroupname.finish('嗯, 很棒的名字呢~')


leavegroup = on_command(
    "退群",
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)


@leavegroup.handle([Cooldown(5, prompt=flmt_notice)])
async def _(event: MessageEvent, bot: Bot, arg: Message = CommandArg()):
    gids = arg.extract_plain_text().strip().split()

    if gids:
        for gid in gids:
            if not is_number(gid):
                await leavegroup.finish("群号必须为数字", at_sender=True)
        msg = ''
        for gid in gids:
            try:
                await bot.set_group_leave(group_id=int(gid), is_dismiss=True)
                logger.info(f"退出群聊 {gid} 成功")
                msg += f"\n退出群聊 {gid} 成功"
            except ActionFailed as e:
                e1 = err_info(e)
                logger.warning(f"退出群聊 {gid} 失败: {e1}")
                msg += f"\n退出群聊 {gid} 失败: {e1}"
        await leavegroup.send('', at_sender=True)
        await leavegroup.finish(msg.lstrip())

    elif isinstance(event, GroupMessageEvent):
        group_id = event.group_id
        try:
            await bot.set_group_leave(group_id=group_id, is_dismiss=True)
            logger.info(f"退出群聊 {group_id} 成功")
            msg = f"退出群聊 {group_id} 成功"
        except ActionFailed as e:
            e1 = err_info(e)
            logger.warning(f"退出群聊 {group_id} 失败: {e1}")
            msg = f"退出群聊 {group_id} 失败: {e1}"
        await bot.send_private_msg(user_id=event.user_id, message=msg)

    else:
        await leavegroup.finish("需要群号")


specialtitle = on_command(
    "设置头衔",
    aliases={'修改头衔'},
    permission=SUPERUSER | GROUP_OWNER,
    priority=1,
    block=True
)


@specialtitle.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    uids = [int(at.data['qq']) for at in event.get_message()['at']]
    if not uids:
        logger.warning('未指定要修改头衔的对象!')
        return
    content = unescape(arg.extract_plain_text().strip())
    if len(bytes(content, encoding='utf-8')) > 18:
        await specialtitle.finish('头衔太长啦!')
    x = True
    try:
        for uid in uids:
            await bot.set_group_special_title(
                group_id=event.group_id,
                user_id=uid,
                special_title=content,
                duration=-1
            )
    except ActionFailed as e:
        logger.warning(err_info(e))
        x = None
    await specialtitle.finish(x if not x else '嗯, 很棒的头衔呢~')


applyspecialtitle = on_command(
    "申请头衔",
    priority=5,
    block=True
)


@applyspecialtitle.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    content = unescape(arg.extract_plain_text().strip())
    if len(bytes(content, encoding='utf-8')) > 18:
        await applyspecialtitle.finish('头衔太长啦!')
    x = True
    try:
        await bot.set_group_special_title(
            group_id=event.group_id,
            user_id=event.user_id,
            special_title=content,
            duration=-1
        )
    except ActionFailed as e:
        logger.warning(err_info(e))
        x = None
    await applyspecialtitle.finish(x if not x else '嗯, 很棒的头衔呢~')


setgroupportrait = on_command(
    "设置群头像",
    rule=to_me(),
    permission=SUPERUSER | GROUP_OWNER | GROUP_OWNER,
    priority=1,
    block=True
)


@setgroupportrait.handle([Cooldown(5, prompt=flmt_notice)])
async def _(event: GroupMessageEvent, matcher: Matcher) -> None:
    imgs = extract_image_urls(event.get_message())
    if imgs:
        matcher.set_arg("IMAGES", event.get_message())


@setgroupportrait.got("IMAGES", prompt="请发送图片")
async def _(bot: Bot, event: GroupMessageEvent) -> None:
    imgs = extract_image_urls(event.get_message())
    print(imgs)
    if imgs:
        try:
            await bot.set_group_portrait(group_id=event.group_id, file=imgs[0])
        except ActionFailed as e:
            await setgroupportrait.finish(err_info(e))
        await setgroupportrait.finish('已尝试修改群头像.')
