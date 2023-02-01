from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    GroupMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER,
    unescape,
    ActionFailed,
)
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .utils import (
    flmt_notice,
    err_info,
    is_number,
    format_time,
)


set_name = on_command(
    "设置网名",
    aliases={"设置昵称"},
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)

@set_name.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, arg: Message = CommandArg()):
    name = unescape(arg.extract_plain_text().strip())
    if len(bytes(name, encoding='utf-8')) > 36:
        await set_name.finish('名字太长啦!')
    try:
        await bot.set_qq_profile(nickname=name)
    except ActionFailed as e:
        await set_name.finish(err_info(e))
    await set_name.finish('昵称设置成功~')


get_stranger = on_command(
    "查找好友",
    aliases={"查找用户"},
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)

@get_stranger.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, arg: Message = CommandArg()):
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        await get_stranger.finish('用法: \n查找好友 qq qq1 qq2 ...')
    for uid in uids:
        if not is_number(uid):
            await get_stranger.finish('参数错误, id必须是数字..')
    msg, err = [], "\n"
    for uid in uids:
        try:
            user = await bot.get_stranger_info(user_id=int(uid), no_cache=True)
        except ActionFailed as e:
            err += f"\n{uid}: {err_info(e)}"
            continue
        msg.append(f"user: {user['user_id']}\n"
          f"QID: {user['qid']}\n"
          f"昵称: {user['nickname']}\n"
          f"性别: {user['sex']}\n"
          f"年龄: {user['age']}\n"
          f"等级: {user['level']}")
    await get_stranger.finish(('\n\n'.join(msg)+(err if not err.isspace() else '')).strip())


get_group = on_command(
    "查找群",
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)

@get_group.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, arg: Message = CommandArg()):
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        await get_group.finish('用法: \n查找群 qq qq1 qq2 ...')
    for uid in uids:
        if not is_number(uid):
            await get_group.finish('参数错误, id必须是数字..')
    msg, err = [], "\n"
    for uid in uids:
        try:
            g = await bot.get_group_info(group_id=int(uid), no_cache=True)
        except ActionFailed as e:
            err += f"\n{uid}: {err_info(e)}"
            continue
        _time = (
            format_time(g['group_create_time'])
            if g['group_create_time'] else 'unknown'
        )
        _level = g['group_level'] if g['group_level'] else 'unknown'
        _member = g['member_count'] if g['member_count'] else 'unknown'
        max_member = g['max_member_count'] if g['max_member_count'] else 'unknown'
        msg.append(f"group: {g['group_id']}\n"
                   f"群名: {g['group_name']}\n"
                   f"备注: {g.get('group_memo', '')}\n"
                   f"创建: {_time}\n"
                   f"等级: {_level}\n"
                   f"人数: {_member}\n"
                   f"容量: {max_member}")
    await get_group.finish(('\n\n'.join(msg)+(err if not err.isspace() else '')).strip())


cls_group = on_command(
    "查看所有群",
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)

@cls_group.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot):
    gl = await bot.get_group_list()
    msg = '\n'.join(["{group_id} {group_name}".format_map(g) for g in gl])
    await cls_group.finish(f"bot:{bot.self_id}\n共{len(gl)}个群聊\n{msg}")


cls_friend = on_command(
    "查看所有好友",
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)

@cls_friend.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot):
    gl = await bot.get_friend_list()
    msg = '\n'.join([
        "user: {user_id}\n昵称: {nickname}\n备注: {remark}".format_map(g)
        for g in gl
    ])
    await cls_friend.finish(f"共{len(gl)}个好友\n{msg}")


unidirectional_friend = on_command(
    "查看单向好友",
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)

@unidirectional_friend.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot):
    gl = await bot.get_unidirectional_friend_list()
    msg = '\n'.join([
        "user: {user_id}\n昵称: {nickname}\n来源: {source}".format_map(g)
        for g in gl
    ])
    await unidirectional_friend.finish(f"共{len(gl)}个单向好友\n{msg}")


del_friend = on_command(
    "删除好友",
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)

@del_friend.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, arg: Message = CommandArg()):
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        await del_friend.finish('用法: \n删除好友 qq qq1 qq2 ...')
    for uid in uids:
        if not is_number(uid):
            await del_friend.finish('参数错误, id必须是数字..')

    x, msg = 0, []
    for uid in uids:
        try:
            await bot.delete_friend(user_id=uid)
        except ActionFailed as e:
            msg.append(f"\n{uid}: {err_info(e)}")
            continue
        x += 1

    await del_friend.finish(f"已删除{x}个好友\n"+'\n'.join(msg))


del_nidirectional = on_command(
    "删除单向好友",
    rule=to_me(),
    permission=SUPERUSER,
    priority=1,
    block=True
)

@del_nidirectional.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, arg: Message = CommandArg()):
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        await del_nidirectional.finish('用法: \n删除单向好友 qq qq1 qq2 ...')
    for uid in uids:
        if not is_number(uid):
            await del_nidirectional.finish('参数错误, id必须是数字..')

    x, msg = 0, []
    for uid in uids:
        try:
            await bot.delete_nidirectional_friend(user_id=uid)
        except ActionFailed as e:
            msg.append(f"\n{uid}: {err_info(e)}")
            continue
        x += 1

    await del_nidirectional.finish(f"已删除{x}个单向好友\n"+'\n'.join(msg))


cls_group_member = on_command(
    "查看群员列表",
    rule=to_me(),
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    priority=1,
    block=True
)

@cls_group_member.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent):
    gl = await bot.get_group_member_list(group_id=event.group_id)
    node = [{
        "type": "node",
        "data": {
            "name": g["card"] if g["card"] else g["nickname"],
            "uin": str(g["user_id"]),
            "content": f"""
user: {g['user_id']}
昵称: {g['nickname']}
备注: {g['card']}
专属头衔: {g['title']}
禁言到期: {
    format_time(g['shut_up_timestamp'])
    if g['shut_up_timestamp'] else 'NaN'
}
""".strip()
        }
    } for g in gl]
    try:
        await bot.send_group_forward_msg(group_id=event.group_id, messages=node)
    except ActionFailed as e:
        await cls_group_member.send(err_info(e))
    await cls_group_member.finish(f"本群共{len(gl)}个成员")


talkative = on_command(
    "召唤龙王",
    priority=5,
    block=True
)

@talkative.handle([Cooldown(5, prompt=flmt_notice)])
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        user = (await bot.get_group_honor_info(group_id=event.group_id, type="talkative"))["current_talkative"]["user_id"]
    except ActionFailed as e:
        await talkative.finish(err_info(e))
    await talkative.finish(MessageSegment.at(user))
