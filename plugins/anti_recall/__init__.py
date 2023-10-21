import ujson as json
from pathlib import Path
from nonebot import on_notice, on_command
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot, 
    MessageEvent,
    GroupRecallNoticeEvent, 
    FriendRecallNoticeEvent, 
    Message,
)

from .utils import recall_msg_dealer, MessageChecker


switch_file = Path() / 'data' / 'anti_recall' / 'anti_recall.json'
switch_file.parent.mkdir(parents=True, exist_ok=True)

switch = (
    json.loads(switch_file.read_text('utf-8'))
    if switch_file.is_file()
    else {}
)


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

    if not switch.get(self_id):
        switch.update({
            self_id: False
        })
        save_switch()

    return self_id


enable_anti_recall = on_command(
    '开启防撤回',
    aliases={'开启反撤回', '启用防撤回', '启用反撤回'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@enable_anti_recall.handle()
async def _(event: MessageEvent):
    self_id = check_self_id(event.self_id)
    switch[self_id] = True
    save_switch()
    await enable_anti_recall.finish('反撤回已开启.')


disable_anti_recall = on_command(
    '关闭防撤回',
    aliases={'关闭反撤回', '禁用防撤回', '禁用反撤回'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@disable_anti_recall.handle()
async def _(event: MessageEvent):
    self_id = check_self_id(event.self_id)
    switch[self_id] = False
    save_switch()
    await disable_anti_recall.finish('反撤回已关闭.')


recall_event = on_notice(priority=1, block=False)

@recall_event.handle()
async def _(bot: Bot, event: FriendRecallNoticeEvent):
    self_id = check_self_id(event.self_id)
    if not switch[self_id]:
        return

    if event.is_tome():
        return

    try:
        repo = await bot.get_msg(message_id=event.message_id)
    except Exception:
        return

    logger.debug(f"Recall raw msg:\n{repo}")
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
    msg = f"{user}@[私聊]\n撤回了\n{m}"
    for superuser in bot.config.superusers:
        await bot.send_private_msg(user_id=int(superuser), message=Message(msg))


@recall_event.handle()
async def _(bot: Bot, event: GroupRecallNoticeEvent):
    self_id = check_self_id(event.self_id)
    if not switch[self_id]:
        return

    if event.is_tome():
        return

    try:
        repo = await bot.get_msg(message_id=event.message_id)
    except Exception:
        return

    logger.debug(f"Recall raw msg:\n{repo}")
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
    msg = f"{user}@[群聊:{group}]\n撤回了\n{m}"
    for superuser in bot.config.superusers:
        await bot.send_private_msg(user_id=int(superuser), message=Message(msg))
