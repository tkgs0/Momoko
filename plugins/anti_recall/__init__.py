import unicodedata
import ujson as json
from pathlib import Path
from typing import Literal
from nonebot import on_notice, on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupRecallNoticeEvent, 
    FriendRecallNoticeEvent, 
    Message,
)

from .utils import recall_msg_dealer, MessageChecker


__help__: str = """

禁用(启用)反撤回
禁用(启用)私聊(群聊)反撤回 qq qq1 qq2 ...
重置反撤回
反撤回状态

{
    "self_id": {
        enable: True,
        private: [],
        group: []
    }
}

"""


switch_file = Path() / 'data' / 'anti_recall' / 'anti_recall.json'
switch_file.parent.mkdir(parents=True, exist_ok=True)

switch = (
    json.loads(switch_file.read_text('utf-8'))
    if switch_file.is_file()
    else {}
)

template = {
    'enable': True,
    'private': [],
    'group': []
}


def save_switch() -> None:
    switch_file.write_text(
        json.dumps(
            switch,
            ensure_ascii=False,
            escape_forward_slashes=False,
            indent=2
        ),
        encoding='utf-8'
    )


def check_self_id(self_id) -> str:
    self_id = f'{self_id}'
    temp: dict = {}
    temp.update(template)

    try:
        if not switch.get(self_id):
            switch.update({
                self_id: temp
            })
            save_switch()
        for i in template:
            if switch[self_id].get(i) == None:
                switch[self_id].update({i: temp[i]})
                save_switch()
    except Exception:
        switch.update({
            self_id: temp
        })
        save_switch()

    return self_id


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


enable_anti_recall = on_command(
    '开启防撤回',
    aliases={'开启反撤回', '启用防撤回', '启用反撤回'},
    permission=SUPERUSER,
    priority=1,
    block=True
)

@enable_anti_recall.handle()
async def _(event: MessageEvent):
    self_id = check_self_id(event.self_id)
    switch[self_id]['enable'] = True
    save_switch()
    await enable_anti_recall.finish('反撤回已开启.')


disable_anti_recall = on_command(
    '关闭防撤回',
    aliases={'关闭反撤回', '禁用防撤回', '禁用反撤回'},
    permission=SUPERUSER,
    priority=1,
    block=True
)

@disable_anti_recall.handle()
async def _(event: MessageEvent):
    self_id = check_self_id(event.self_id)
    switch[self_id]['enable'] = False
    save_switch()
    await disable_anti_recall.finish('反撤回已关闭.')


add_private = on_command(
    '启用私聊反撤回',
    aliases={'启用私聊防撤回', '开启私聊反撤回', '开启私聊防撤回'},
    permission=SUPERUSER,
    priority=1,
    block=True
)

@add_private.handle()
async def add_user_list(event: MessageEvent, arg: Message = CommandArg()):
    msg = handle_msg(event.self_id, arg, 'add', 'private')
    await add_private.finish(msg)


del_private = on_command(
    '禁用私聊反撤回',
    aliases={'禁用私聊防撤回', '关闭私聊反撤回', '关闭私聊防撤回'},
    permission=SUPERUSER,
    priority=1,
    block=True
)

@del_private.handle()
async def del_user_list(event: MessageEvent, arg: Message = CommandArg()):
    msg = handle_msg(event.self_id, arg, 'del', 'private')
    await del_private.finish(msg)


add_group = on_command(
    '启用群聊反撤回',
    aliases={'启用群聊防撤回', '开启群聊反撤回', '开启群聊防撤回'},
    permission=SUPERUSER,
    priority=1,
    block=True
)

@add_group.handle()
async def add_group_list(event: MessageEvent, arg: Message = CommandArg()):
    msg = handle_msg(event.self_id, arg, 'add', 'group')
    await add_group.finish(msg)


del_group = on_command(
    '禁用群聊反撤回',
    aliases={'禁用群聊防撤回', '关闭群聊反撤回', '关闭群聊防撤回'},
    permission=SUPERUSER,
    priority=1,
    block=True
)

@del_group.handle()
async def del_group_list(event: MessageEvent, arg: Message = CommandArg()):
    msg = handle_msg(event.self_id, arg, 'del', 'group')
    await del_group.finish(msg)


reset_switch = on_command('重置反撤回', permission=SUPERUSER, priority=1, block=True)

@reset_switch.got('FLAG', prompt='确定重置反撤回服务? (y/n)')
async def reset_list(event: MessageEvent, matcher: Matcher):
    flag = matcher.state['FLAG'].extract_plain_text().strip()

    uid = check_self_id(event.self_id)

    if flag.lower() in ['y', 'yes', 'true']:
        switch.pop(uid)
        save_switch()
        await reset_switch.finish(f'已重置反撤回服务.')
    else:
        await reset_switch.finish('操作已取消')


check_private = on_command(
    '反撤回状态',
    aliases={'防撤回状态'},
    permission=SUPERUSER,
    priority=1,
    block=True
)

@check_private.handle()
async def check_user_list(event: MessageEvent):
    self_id = check_self_id(event.self_id)
    uids = switch[self_id]['private']
    gids = switch[self_id]['group']
    msg = f"服务状态: {'启用' if switch[self_id]['enable'] else '禁用'}\nprivate: {', '.join(uids)}\ngroup: {', '.join(gids)}"
    await check_private.finish(msg)


recall_event = on_notice(priority=1, block=False)

@recall_event.handle()
async def _(bot: Bot, event: FriendRecallNoticeEvent):
    self_id = check_self_id(event.self_id)
    user = str(event.user_id)

    if not switch[self_id]['enable'] or not user in switch[self_id]['private'] or event.is_tome():
        return

    try:
        repo = await bot.get_msg(message_id=event.message_id)
    except Exception:
        return

    logger.debug(f"Recall raw msg:\n{repo}")
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
    self_id = check_self_id(event.self_id)
    user = str(event.user_id)
    group = str(event.group_id)

    if not switch[self_id]['enable'] or not group in switch[self_id]['group'] or event.is_tome():
        return

    try:
        repo = await bot.get_msg(message_id=event.message_id)
    except Exception:
        return

    logger.debug(f"Recall raw msg:\n{repo}")
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


def handle_msg(
    self_id,
    arg,
    mode: Literal['add', 'del'],
    type_: Literal['group', 'private'],
) -> str:
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        return '用法: \n禁用(启用)私聊(群聊)反撤回 qq qq1 qq2 ...'
    for uid in uids:
        if not is_number(uid):
            return '参数错误, id必须是数字..'
    msg = handle_switch(self_id, uids, mode, type_)
    return msg


def handle_switch(
    self_id,
    uids: list,
    mode: Literal['add', 'del'],
    type_: Literal['group', 'private'],
) -> str:
    self_id = check_self_id(self_id)

    types = {
        'group': '群聊',
        'private': '私聊',
    }

    if mode == 'add':
        switch[self_id][type_].extend(uids)
        switch[self_id][type_] = list(set(switch[self_id][type_]))
        _mode = '启用'
    elif mode == 'del':
        switch[self_id][type_] = [uid for uid in switch[self_id][type_] if uid not in uids]
        _mode = '禁用'
    save_switch()
    _type = types[type_]
    return f"已对 {len(uids)} 个{_type}{_mode}反撤回: {', '.join(uids)}"
