from pathlib import Path
from typing import Literal
import ujson as json
import asyncio

from nonebot import logger, on_command, get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import CommandArg, ArgStr
from nonebot.permission import SUPERUSER
from nonebot.exception import IgnoredException
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    ActionFailed,
)
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .config import Config
from . import lolicon, acggov

usage: str = """

指令表:
    /setu {数量} {关键词}

    私聊(群聊)启用(禁用)涩图 qq qq1 qq2 ...
    查看涩图设置
    切换涩图api
    启用(禁用)涩图
    重置涩图

示例:
    /setu
    /setu 3
    /setu 阿波尼亚
    /setu 3 阿波尼亚
    /setu 3 R-18 阿波尼亚 水着

""".strip()


__plugin_meta__ = PluginMetadata(
    name="setu",
    description="🥵",
    usage=usage,
    type="application"
)


setu_config = get_plugin_config(Config)

cooldown: int = setu_config.setu_cooldown
withdraw: int = setu_config.setu_withdraw
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


def save_config() -> None:
    filepath.write_text(json.dumps(enabled), encoding='utf-8')


setu_cd = [Cooldown(cooldown, prompt='慢...慢一..点❤')] if cooldown > 0 else None

def setu_wd(bot: Bot, msg_id: int) -> None:
    if withdraw < 1:
        return
    loop = asyncio.get_running_loop()
    loop.call_later(
        withdraw if withdraw < 120 else 110,  # 消息撤回等待时间 单位秒
        lambda: loop.create_task(bot.delete_msg(message_id=msg_id)),
    )


def err_info(e: ActionFailed) -> str:
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)


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


@run_preprocessor
def setu_processor(matcher: Matcher, event: MessageEvent):
    gid: int = event.group_id if isinstance(event, GroupMessageEvent) else 0
    uid: int = event.user_id if not gid else 0

    if matcher.plugin_name == 'setu' and matcher.priority > 2:
        if gid and str(gid) not in enabled['grouplist']:
            logger.debug(f'未在群聊 {gid} 启用色图.')
            raise IgnoredException('setu is disabled.')
        if not gid and str(uid) not in enabled['userlist']:
            logger.debug(f'未在私聊 {uid} 启用色图.')
            raise IgnoredException('setu is disabled.')


setu = on_command(
    '/setu',
    aliases={'涩图', '瑟图', '色图'},
    priority=5,
    block=True
)


@setu.handle(setu_cd)
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):

    gid: int = event.group_id if isinstance(event, GroupMessageEvent) else 0
    uid: int = event.user_id if not gid else 0

    await setu.send('loading...', at_sender=True)
    content = await get__setu(event, args)
    if not content[1]:
        await setu.finish(content[0])
    try:
        setu_wd(bot, (await bot.send_forward_msg(
            user_id=uid, group_id=gid, messages=content[0])
        )['message_id'])
    except ActionFailed as e:
        logger.error(repr(e))
        await setu.finish(err_info(e))


async def get__setu(
    event: MessageEvent,
    args: Message = CommandArg()
) -> list:
    uid = event.user_id
    name = event.sender.card or event.sender.nickname or '老色批'
    keyword = args.extract_plain_text().strip().split()
    num = (
        int(keyword.pop(0))
        if keyword and is_number(keyword[0])
        else 1
    )

    get_api = lolicon if enabled['api'] == 'lolicon' else acggov
    content = await get_api.get_setu(
        uid = uid,
        name = name,
        keyword = keyword or ['R-18'],
        img = num,
        pixproxy = pixproxy,
        r18 = lolicon_r18,
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

