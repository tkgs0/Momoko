import time, random, asyncio
from pathlib import Path
from typing import Literal
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from nonebot import on_notice, on_request, on_command
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    PrivateMessageEvent,
    GroupMessageEvent,
    GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent,
    FriendRequestEvent,
    GroupRequestEvent,
    GROUP_ADMIN,
    GROUP_OWNER,
    unescape,
    ActionFailed,
)
from nonebot.adapters.onebot.v11.helpers import Cooldown


from .utils import flmt_notice, err_info, is_number, format_time


filepath = Path() / 'data' / 'reqlist' / 'reqlist.json'
filepath.parent.mkdir(parents=True, exist_ok=True)

reqlist = (
    json.loads(filepath.read_text('utf-8'))
    if filepath.is_file()
    else {
        'auto_approve': {'group': [{}, -1], 'user': -1},
        'group': {'add': {}, 'invite': {}},
        'user': {},
    }
)


def save_reqlist() -> None:
    filepath.write_text(json.dumps(reqlist), encoding='utf-8')


fdgr = on_request(priority=1, block=False)

@fdgr.handle()
async def _(bot: Bot, event: FriendRequestEvent):

    if type(auto := reqlist['auto_approve']['user']) == bool:
        await bot.set_friend_add_request(flag=event.flag, approve=auto)
    else:
        reqlist['user'].update({
            event.user_id: {
                'time': event.time,
                'self_id': event.self_id,  # 机器人id
                'user_id': event.user_id,  # 请求人id
                'comment': event.comment,
                'flag': event.flag
            }
        })
        save_reqlist()

    nickname = (
        await bot.get_stranger_info(user_id=event.user_id, no_cache=True)
    )['nickname']
    _time = format_time(event.time)
    msg = (
        '⚠收到一条好友请求:\n'
        f'user: {event.user_id}\n'
        f'name: {nickname}\n'
        f'time: {_time}\n'
        f'自动同意/拒绝: {auto}\n'
        '(-1为不处理)\n'
        f'验证信息:\n'
        f'{event.comment}'
    )
    for supersu in bot.config.superusers:
        await bot.send_private_msg(user_id=int(supersu), message=msg)

@fdgr.handle()
async def _(bot: Bot, event: GroupRequestEvent):

    nickname = (
        await bot.get_stranger_info(user_id=event.user_id, no_cache=True)
    )['nickname']
    _time = format_time(event.time)

    auto = reqlist['auto_approve']['group']

    if event.sub_type == 'add':  # 当类型为入群申请
        auto1 = auto[0].get(event.group_id)
        if type(auto1) == bool:
            await bot.set_group_add_request(
                flag=event.flag, sub_type='add', approve=auto1)
        else:
            reqlist['group']['add'].update({
                event.flag: {
                    'time': event.time,
                    'self_id': event.self_id,  # 机器人id
                    'user_id': event.user_id,  # 请求人id
                    'group_id': event.group_id,  # 目标群号
                    'comment': event.comment,
                    'flag': event.flag,
                }
            })
            save_reqlist()

        msg = (
            '⚠收到一条入群申请:\n'
            f'flag: {event.flag}\n'
            f'user: {event.user_id}\n'
            f'name: {nickname}\n'
            f'time: {_time}\n'
            f'自动同意/拒绝: {auto[0].get(event.group_id)}\n'
            '(None为不处理)\n'
            f'验证信息:\n'
            f'{event.comment}'
        )
        await bot.send_group_msg(group_id=event.group_id, message=msg)

    if event.sub_type == 'invite':  # 当类型为拉群邀请
        if type(auto[1]) == bool:
            await asyncio.sleep(random.random()+2.5)
            await bot.set_group_add_request(
                flag=event.flag, sub_type='invite', approve=auto[1])
        else:
            reqlist['group']['invite'].update({
                event.flag: {
                    'time': event.time,
                    'self_id': event.self_id,  # 机器人id
                    'user_id': event.user_id,  # 请求人id
                    'group_id': event.group_id,  # 目标群号
                    'comment': event.comment,
                    'flag': event.flag,
                }
            })
            save_reqlist()

        group_name = (
            await bot.get_group_info(group_id=event.group_id, no_cache=True)
        )['group_name']
        msg = (
            '⚠收到一条拉群邀请:\n'
            f'flag: {event.flag}\n'
            f'user: {event.user_id}\n'
            f'name: {nickname}\n'
            f'group: {event.group_id}\n'
            f'name: {group_name}\n'
            f'time: {_time}\n'
            f'自动同意/拒绝: {auto[1]}\n'
            '(-1为不处理)\n'
            f'验证信息:\n'
            f'{event.comment}'
        )
        for supersu in bot.config.superusers:
            await bot.send_private_msg(user_id=int(supersu), message=msg)


async def friend(
    bot: Bot,
    approve: bool,
    arg: Message = CommandArg()
) -> str:
    args = arg.extract_plain_text().strip().split(maxsplit=1)
    if not args:
        return '用法: \n同意(拒绝)好友 QQ号 备注\n\n(备注可留空)'

    uid = args[0]
    remark = unescape(args[1]) if len(args) > 2 else ''
    if not is_number(uid):
        return '参数错误! QQ号必须为数字.'
    if len(bytes(remark, encoding='utf-8')) > 60:
        return '备注太长啦!'

    try:
        req = reqlist['user'].pop(int(uid))
    except KeyError:
        return '事件不存在或已被清理.'
    flag = req.get('flag')
    save_reqlist()

    try:
        await bot.set_friend_add_request(
            flag=flag, approve=approve, remark=remark)
    except ActionFailed as e:
        return err_info(e)
    except Exception as e:
        return repr(e)

    _mode = '同意' if approve else '拒绝'
    return f'已{_mode}好友{uid}.'


async def group(
    bot: Bot,
    mode: Literal['add', 'invite'],
    approve: bool,
    arg: Message = CommandArg(),
    group: int = 0,
) -> str:
    args = arg.extract_plain_text().strip().split(maxsplit=1)
    if not args:
        return (
            '用法: \n'
            '同意(拒绝)入群 FLAG 理由\n'
            '同意(拒绝)拉群 FLAG\n\n'
            '(理由可留空)'
        )

    flag = args[0]
    reason = unescape(args[1]) if len(args) > 2 else ''
    if not is_number(flag):
        return '参数错误! FLAG 必须为数字.'
    if len(bytes(reason, encoding='utf-8')) > 75:
        return '理由太长啦!'

    req = reqlist['group'][mode].get(flag)
    if not req:
        return '事件不存在或已被清理.'
    if group and group != req['group_id']:
        return '不可跨群处理.'
    reqlist['group'][mode].pop(flag)
    save_reqlist()

    try:
        await bot.set_group_add_request(
            flag=flag, sub_type=mode, approve=approve, reason=reason)
    except ActionFailed as e:
        return err_info(e)
    except Exception as e:
        return repr(e)

    ap = '同意' if approve else '拒绝'
    _mode = '入群' if mode == 'add' else '拉群'
    gid = req["group_id"] if mode == "invite" else ""
    return f'已{ap}用户{req["user_id"]}{_mode}{gid}.'


approve_friend = on_command(
    '/同意好友',
    aliases={'/接受好友'},
    permission=SUPERUSER,
    priority=1,
    block=True
)


@approve_friend.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, args: Message = CommandArg()):
    msg = await friend(bot, True, args)
    await approve_friend.finish(msg)


reject_friend = on_command(
    '/拒绝好友',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@reject_friend.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, args: Message = CommandArg()):
    msg = await friend(bot, False, args)
    await reject_friend.finish(msg)


approve_group_a = on_command(
    '/同意入群',
    aliases={'/接受入群'},
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    priority=1,
    block=True
)


@approve_group_a.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    msg = await group(bot, 'add', True, args, event.group_id)
    await approve_group_a.finish(msg)


reject_group_a = on_command(
    '/拒绝入群',
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    priority=1,
    block=True
)


@reject_group_a.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    msg = await group(bot, 'add', False, args, event.group_id)
    await reject_group_a.finish(msg)


approve_group_i = on_command(
    '/同意拉群',
    aliases={'/接受拉群'},
    permission=SUPERUSER,
    priority=1,
    block=True
)


@approve_group_i.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, args: Message = CommandArg()):
    msg = await group(bot, 'invite', True, args)
    await approve_group_i.finish(msg)


reject_group_i = on_command(
    '/拒绝拉群',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@reject_group_i.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, args: Message = CommandArg()):
    msg = await group(bot, 'invite', False, args)
    await reject_group_i.finish(msg)


read_fdreq = on_command(
    '/查看好友请求',
    aliases={'/查看好友申请'},
    permission=SUPERUSER,
    priority=1,
    block=True
)


@read_fdreq.handle([Cooldown(5, prompt=flmt_notice)])
async def _():

    msg = ''
    for i in reqlist['user']:
        user = reqlist['user'].get(i)
        msg += f'\nuser: {user["user_id"]}\n验证信息: {user["comment"]}'
    
    await read_fdreq.finish(
        f'自动处理: {reqlist["auto_approve"]["user"]}'
        '\n-1: 不处理'
        '\nTrue: 自动同意'
        '\nFalse: 自动拒绝'
        f'\n\n当前存在的好友请求: {msg}'
    )


read_grreq = on_command(
    '/查看群聊请求',
    aliases={'/查看群聊申请'},
    permission=SUPERUSER,
    priority=1,
    block=True
)


@read_grreq.handle([Cooldown(5, prompt=flmt_notice)])
async def _():

    gra = ''
    for i in reqlist['group']['add']:
        g = reqlist['group']['add'].get(i)
        gra += (
            f'\nFLAG: {g["flag"]}'
            f'\n请求人: {g["user_id"]}'
            f'\n目标群: {g["group_id"]}'
            f'\n验证信息: {g["comment"]}'
        )
    auto1 = '\n' + '\n'.join([
        f'{i}: {reqlist["auto_approve"]["group"][0].get(i)}'
        for i in reqlist["auto_approve"]["group"][0]
    ])
    msg = f'\n入群申请:\n自动处理: {auto1 if not auto1.isspace() else "-1"}' + gra

    gri = ''
    for i in reqlist['group']['invite']:
        g = reqlist['group']['invite'].get(i)
        gri += (
            f'\nFLAG: {g["flag"]}'
            f'\n请求人: {g["user_id"]}'
            f'\n目标群: {g["group_id"]}'
            f'\n验证信息: {g["comment"]}'
        )
    msg1 = f'\n\n拉群邀请:\n自动处理: {reqlist["auto_approve"]["group"][1]}' + gri

    await read_grreq.finish(
        f'当前存在的群聊请求: \n{msg+msg1}'
        '\n\n-1: 不处理'
        '\nTrue: 自动同意'
        '\nFalse: 自动拒绝'
    )


reset_fdreq = on_command(
    '/清空好友请求',
    aliases={'/清空好友申请'},
    permission=SUPERUSER,
    priority=1,
    block=True
)


@reset_fdreq.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['user'].clear()
    save_reqlist()
    await reset_fdreq.finish('已清空好友请求.')


reset_grreqa = on_command(
    '/清空入群请求',
    aliases={'/清空入群申请'},
    permission=SUPERUSER,
    priority=1,
    block=True
)


@reset_grreqa.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['group']['add'].clear()
    save_reqlist()
    await reset_grreqa.finish('已清空入群请求.')


reset_grreqi = on_command(
    '/清空拉群请求',
    aliases={'/清空拉群邀请'},
    permission=SUPERUSER,
    priority=1,
    block=True
)


@reset_grreqi.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['group']['invite'].clear()
    save_reqlist()
    await reset_grreqi.finish('已清空拉群请求')


approve_autofd = on_command(
    '/好友自动同意',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@approve_autofd.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['auto_approve']['user'] = True
    save_reqlist()
    await approve_autofd.finish('已开启好友申请自动同意.')


reject_autofd = on_command(
    '/好友自动拒绝',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@reject_autofd.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['auto_approve']['user'] = False
    save_reqlist()
    await reject_autofd.finish('已开启好友申请自动拒绝.')



off_autofd = on_command(
    '/关闭好友自动',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@off_autofd.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['auto_approve']['user'] = -1
    save_reqlist()
    await off_autofd.finish('已关闭自动处理好友请求.')


approve_autogra = on_command(
    '/入群自动同意',
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    priority=1,
    block=True
)


@approve_autogra.handle([Cooldown(5, prompt=flmt_notice)])
async def _(event: GroupMessageEvent):
    reqlist['auto_approve']['group'][0].update({event.group_id: True})
    save_reqlist()
    await approve_autogra.finish('已开启入群申请自动同意.')


reject_autogra = on_command(
    '/入群自动拒绝',
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    priority=1,
    block=True
)


@reject_autogra.handle([Cooldown(5, prompt=flmt_notice)])
async def _(event: GroupMessageEvent):
    reqlist['auto_approve']['group'][0].update({event.group_id: False})
    save_reqlist()
    await reject_autogra.finish('已开启入群申请自动拒绝.')


off_autogra = on_command(
    '/关闭入群自动',
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    priority=1,
    block=True
)


@off_autogra.handle([Cooldown(5, prompt=flmt_notice)])
async def _(event: GroupMessageEvent):
    try:
        reqlist['auto_approve']['group'][0].pop(event.group_id)
    except KeyError:
        pass
    save_reqlist()
    await off_autogra.finish('已关闭自动处理入群请求.')


approve_autogri = on_command(
    '/拉群自动同意',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@approve_autogri.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['auto_approve']['group'][1] = True
    save_reqlist()
    await approve_autogri.finish('已开启拉群邀请自动同意.')


reject_autogri = on_command(
    '/拉群自动拒绝',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@reject_autogri.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['auto_approve']['group'][1] = False
    save_reqlist()
    await reject_autogri.finish('已开启拉群邀请自动拒绝.')


off_autogri = on_command(
    '/关闭拉群自动',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@off_autogri.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['auto_approve']['group'][1] = -1
    save_reqlist()
    await off_autogri.finish('已关闭自动处理拉群请求')


reset_auto = on_command(
    '/重置请求自动',
    permission=SUPERUSER,
    priority=1,
    block=True
)


@reset_auto.handle([Cooldown(5, prompt=flmt_notice)])
async def _():
    reqlist['auto_approve'].clear()
    reqlist['auto_approve'].update({'group': [{}, -1], 'user': -1})
    save_reqlist()
    await reset_auto.finish('已重置请求自动处理开关')


group_member_event = on_notice(priority=1)

@group_member_event.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    _time = time.time()
    if event.user_id == event.self_id:
        for i in reqlist['group']['invite']:
            if (j := reqlist['group']['invite'].get(i,{})).get('group_id') == event.group_id and str(j['user_id']) not in bot.config.superusers and _time - j['time'] < 2:
                await group_member_event.send('⚠Error!!!\n群聊邀请与入群时间差小于2秒, 触发自动退群机制!')
                await bot.set_group_leave(group_id=event.group_id)
    else:
        await asyncio.sleep(random.random()*2+1)
        msg = '欢迎~, 以下为本群群规\n' + \
            MessageSegment.image(file='https://code.gitlink.org.cn/SmartBrain/test/raw/branch/main/7f9b8412f8332096cea00a563aba54ac.jpg')
        await group_member_event.finish('欢迎~', at_sender=True)

@group_member_event.handle()
async def _(event: GroupDecreaseNoticeEvent):
    await asyncio.sleep(random.random()*2+1)
    msg = f'一位不愿透露姓名的网友({event.user_id})离开了我们...'
    await group_member_event.finish(msg)


