from pathlib import Path
from typing import Literal

try:
    import ujson as json
except ModuleNotFoundError:
    import json
import asyncio

from nonebot import on_command, get_driver
from nonebot.log import logger
from nonebot.params import CommandArg, ArgStr
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent
)
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .config import Config
from . import lolicon, acggov


setu_config = Config.parse_obj(get_driver().config.dict())

lolicon_r18: int = setu_config.lolicon_r18
pixproxy: str = setu_config.pixproxy
acggov_token: str = setu_config.acggov_token


filepath = Path() / 'data' / 'setu' / 'setu.json'
filepath.parent.mkdir(parents=True, exist_ok=True)

enabled = (
    json.loads(filepath.read_text('utf-8'))
    if filepath.is_file()
    else {'api': 'lolicon', 'grouplist': [], 'userlist': []}
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


def save_config() -> None:
    filepath.write_text(json.dumps(enabled), encoding='utf-8')


setu = on_command(
    '/setu',
    aliases={'涩图', '瑟图', '色图'},
    priority=5,
    block=True
)


@setu.handle([Cooldown(120, prompt='慢...慢一..点❤')])
async def _(bot: Bot, event: PrivateMessageEvent, args: Message = CommandArg()):
    if not str(uid := event.user_id) in enabled['userlist']:
        return
    await setu.send('正在拉取涩图, 请稍后...', at_sender=True)
    content = await get__setu(event, args)
    if not content[1]:
        await setu.finish(content[0])
    try:
        result = await bot.send_forward_msg(user_id=uid, messages=content[0])
    except Exception as e:
        logger.warning(repr(e))
        await setu.finish('Error: 涩图太涩, 发不出去力...')
    await asyncio.sleep(60)
    await bot.delete_msg(message_id = result["message_id"])


@setu.handle([Cooldown(120, prompt='慢...慢一..点❤')])
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    if not str(gid := event.group_id) in enabled['grouplist']:
        return
    await setu.send('正在拉取涩图, 请稍后...', at_sender=True)
    content = await get__setu(event, args)
    if not content[1]:
        await setu.finish(content[0])
    try:
        result = await bot.send_forward_msg(group_id=gid, messages=content[0])
    except Exception as e:
        logger.warning(repr(e))
        await setu.finish('Error: 涩图太涩, 发不出去力...')
    await asyncio.sleep(60)
    await bot.delete_msg(message_id = result["message_id"])


async def get__setu(
    event: MessageEvent,
    args: Message = CommandArg()
) -> list:
    uid = event.user_id
    name = name if (name := event.sender.nickname) else '一位不愿透露姓名的网友'
    keyword = args.extract_plain_text().strip().split()
    num = (
        int(keyword.pop(0))
        if keyword and is_number(keyword[0])
        else 1
    )

    if enabled['api'] == 'lolicon':
        content = await lolicon.get_setu(
            uid = uid,
            name = name,
            keyword = keyword,
            img = num,
            pixproxy = pixproxy,
            r18 = lolicon_r18
        )
    else:
        content = await acggov.get_setu(
            uid = uid,
            name = name,
            keyword = keyword if keyword else ['R-18'],
            img = num,
            pixproxy = pixproxy,
            token = acggov_token
        )


    return content


def handle_msg(
    arg,
    mode: Literal['add', 'del'],
    type_: Literal['userlist', 'grouplist'],
) -> str:
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        return '用法: \n私聊(群聊)启用(禁用)涩图 qq qq1 qq2 ...'
    for uid in uids:
        if not is_number(uid):
            return '参数错误, id必须是数字..'
    msg = handle_enabled(uids, mode, type_)
    return msg


def handle_enabled(
    uids: list,
    mode: Literal['add', 'del'],
    type_: Literal['userlist', 'grouplist'],
) -> str:
    if mode == 'add':
        enabled[type_].extend(uids)
        enabled[type_] = list(set(enabled[type_]))
        _mode = '启用'
    elif mode == 'del':
        enabled[type_] = [uid for uid in enabled[type_] if uid not in uids]
        _mode = '禁用'
    save_config()
    _type = '私聊' if type_ == 'userlist' else '群聊'
    return f"已在 {len(uids)} 个{_type}会话{_mode}涩图: {', '.join(uids)}"


add_userlist = on_command(
    '私聊启用涩图',
    aliases={'私聊启用色图'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@add_userlist.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    if uids := [at.data['qq'] for at in event.get_message()['at']]:
        msg = handle_enabled(uids, 'add', 'userlist')
        await add_userlist.finish(msg)
    msg = handle_msg(arg, 'add', 'userlist')
    await add_userlist.finish(msg)


add_grouplist = on_command(
    '群聊启用涩图',
    aliases={'群聊启用色图'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@add_grouplist.handle()
async def _(arg: Message = CommandArg()):
    msg = handle_msg(arg, 'add', 'grouplist')
    await add_grouplist.finish(msg)


del_userlist = on_command(
    '私聊禁用涩图',
    aliases={'私聊禁用色图'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@del_userlist.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    if uids := [at.data['qq'] for at in event.get_message()['at']]:
        msg = handle_enabled(uids, 'del', 'userlist')
        await del_userlist.finish(msg)
    msg = handle_msg(arg, 'del', 'userlist')
    await del_userlist.finish(msg)


del_grouplist = on_command(
    '群聊禁用涩图',
    aliases={'群聊禁用色图'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@del_grouplist.handle()
async def _(arg: Message = CommandArg()):
    msg = handle_msg(arg, 'del', 'grouplist')
    await del_grouplist.finish(msg)


check_enabled = on_command(
    '查看色图设置',
    aliases={'查看涩图设置'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@check_enabled.handle()
async def _():
    await check_enabled.finish(f"""
API: {enabled['api']}

当前已启用会话:
<私聊> {len(enabled['userlist'])} 个:
{enabled['userlist']}
<群聊> {len(enabled['grouplist'])} 个:
{enabled['grouplist']}
""".strip())


set_api = on_command(
    '切换色图api',
    aliases={'切换涩图api'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@set_api.handle()
async def _(arg: Message = CommandArg()):
    api = arg.extract_plain_text().strip()
    if api.startswith('lolicon'):
        enabled['api'] = 'lolicon'
    elif api.startswith('acggov'):
        enabled['api'] = 'acggov'
    else:
        enabled['api'] = 'lolicon' if enabled['api'] == 'acggov' else 'acggov'
    save_config()
    await set_api.finish(f'API已切换为{enabled["api"]}')


enable = on_command(
    '启用涩图',
    aliases={'启用色图'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@enable.handle()
async def _(event: GroupMessageEvent):
    handle_enabled([f'{event.group_id}'], 'add', 'grouplist')
    await enable.finish('已启用服务: 涩图')

@enable.handle()
async def _(event: PrivateMessageEvent):
    handle_enabled([f'{event.user_id}'], 'add', 'userlist')
    await enable.finish('已启用服务: 涩图')


disable = on_command(
    '禁用涩图',
    aliases={'禁用色图'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@disable.handle()
async def _(event: GroupMessageEvent):
    handle_enabled([f'{event.group_id}'], 'del', 'grouplist')
    await disable.finish('已禁用服务: 涩图')

@disable.handle()
async def _(event: PrivateMessageEvent):
    handle_enabled([f'{event.user_id}'], 'del', 'userlist')
    await disable.finish('已禁用服务: 涩图')


reset_setu = on_command(
    '重置涩图',
    aliases={'重置色图'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@reset_setu.got('flag', prompt='确定重置涩图服务? (Y/n)')
async def reset_list(flag: str = ArgStr('flag')):
    if flag in ['Y', 'Yes', 'True']:
        enabled['api'] = 'lolicon'
        enabled['userlist'].clear()
        enabled['grouplist'].clear()
        save_config()
        await reset_setu.finish('涩图服务已重置')
    else:
        await reset_setu.finish('操作已取消')

