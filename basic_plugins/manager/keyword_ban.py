import re, string, asyncio
from random import random
from typing import Literal
import sqlite3
import ujson as json
from nonebot import logger, get_driver, on_message, on_command
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
    GROUP_OWNER,
    GROUP_ADMIN,
    ActionFailed
)

from .utils import is_number, err_info, datapath,  ban_user, ban_time as b_time


__help__:str = """
关键词禁言 简陋版
可批量添加多个关键词, 以换行隔开

使用方式:
  关键词(/正则)禁言 XX分(/时/日/月)
  [ocr]
  内容1
  内容2
  内容3

  删除禁言关键词(/正则)
  内容1
  内容2
  内容3

  查看禁言关键词(/正则)

  清理群禁言规则 qq qq1 qq2 ...
  # 用于清理已炸或已退出的群聊残留的规则

  /reset_keyword_ban_db
  # 重置数据库

示例:
  关键词禁言 1天
  吃柠檬
  尼玛
  群主是沙壁
  来点🐍图

  正则禁言 30天
  http(s)?://.*
  .*(是|做).+的(狗|猫)
""".strip()


superusers = get_driver().config.superusers

filepath = datapath / "keyword_ban.db"
filepath.parent.mkdir(parents=True, exist_ok=True)
filepath.touch(exist_ok=True)

kwd_db = sqlite3.connect(filepath)

try:
    kwd_db.execute("select * from kwd_list;")
    kwd_db.execute("select * from regex_list;")
except sqlite3.OperationalError:
    kwd_db.execute('''
        CREATE TABLE kwd_list(
        GROUP_ID   INT      NOT NULL,
        CONTENT    TEXT     NOT NULL,
        OCR        BOOLEAN  NOT NULL,
        BAN_TIME   INT      NOT NULL);
    '''.strip())
    kwd_db.execute('''
        CREATE TABLE regex_list(
        GROUP_ID   INT      NOT NULL,
        CONTENT    TEXT     NOT NULL,
        OCR        BOOLEAN  NOT NULL,
        BAN_TIME   INT      NOT NULL);
    '''.strip())


add_kwd = on_command(
    "关键词禁言",
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=2,
    block=True
)

@add_kwd.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    await add_kwd.finish(handle_msg("kwd_list", True, event.group_id, args))


add_regex = on_command(
    "正则禁言",
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=2,
    block=True
)

@add_regex.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    await add_regex.finish(handle_msg("regex_list", True, event.group_id, args))


del_kwd = on_command(
    "删除禁言关键词",
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=2,
    block=True
)

@del_kwd.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    await del_kwd.finish(handle_msg("kwd_list", False, event.group_id, args))


del_regex = on_command(
    "删除禁言正则",
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=2,
    block=True
)

@del_regex.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    await del_regex.finish(handle_msg("regex_list", False, event.group_id, args))


see_kwd = on_command(
    "查看禁言关键词",
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=2,
    block=True
)
@see_kwd.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if msg := (await see_list("kwd_list", bot, event)):
        await see_kwd.finish(msg)


see_regex = on_command(
    "查看禁言正则",
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=2,
    block=True
)

@see_regex.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if msg := (await see_list("regex_list", bot, event)):
        await see_regex.finish(msg)


clean_gid = on_command(
    "清理群禁言规则",
    permission=SUPERUSER,
    priority=2,
    block=True
)

@clean_gid.handle()
async def _(args: Message = CommandArg()):
    uids: list = args.extract_plain_text().strip().split()
    if not uids:
        await clean_gid.finish('用法: \n清理群禁言规则 qq qq1 qq2 ...')
    for uid in uids:
        if not is_number(uid):
            await clean_gid.finish('参数错误, id必须是数字..')
    for uid in uids:
        kwd_db.execute(f'''
            delete from kwd_list where GROUP_ID={uid};
        '''.strip())
    await clean_gid.finish(f"已删除{len(uids)}个群的禁言规则.")


reset_db = on_command(
    "/reset_keyword_ban_db",
    permission=SUPERUSER,
    priority=2,
    block=True
)

@reset_db.handle()
async def _():
    kwd_db.executescript('''
        DROP TABLE kwd_list;
        DROP TABLE regex_list;
        CREATE TABLE kwd_list(
        GROUP_ID   INT      NOT NULL,
        CONTENT    TEXT     NOT NULL,
        OCR        BOOLEAN  NOT NULL,
        BAN_TIME   INT      NOT NULL);
        CREATE TABLE regex_list(
        GROUP_ID   INT      NOT NULL,
        CONTENT    TEXT     NOT NULL,
        OCR        BOOLEAN  NOT NULL,
        BAN_TIME   INT      NOT NULL);
    '''.strip())
    kwd_db.commit()
    await reset_db.finish("数据库已重置.")


help_ = on_command(
    "/keyban",
    priority=5,
    block=True
)

@help_.handle()
async def _(bot: Bot, event: MessageEvent):
    gid: int = event.group_id if isinstance(event, GroupMessageEvent) else 0
    uid: int = event.user_id if not gid else 0

    node: list = [{
            "type": "node",
            "data": {
                "name": event.sender.card or event.sender.nickname or '老色批',
                "uin": event.user_id,
                "content": __help__
            }
    }]
    await bot.send_forward_msg(group_id=gid, user_id=uid, messages=node)



switch_list_file = datapath / 'keyword_ban_switch_list.json'

switch_list = (
    json.loads(switch_list_file.read_text('utf-8'))
    if switch_list_file.is_file()
    else {}
)


def save_switch_list() -> None:
    switch_list_file.write_text(
        json.dumps(
            switch_list,
            ensure_ascii=False,
            escape_forward_slashes=False,
            indent=2
        ),
        encoding='utf-8'
    )


def check_self_id(self_id) -> str:
    self_id = f'{self_id}'

    if not switch_list.get(self_id):
        switch_list.update({
            self_id: []
        })
        save_switch_list()

    return self_id


enable_keyban = on_command(
    '/启用keyban',
    aliases={'/开启keyban'},
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=2,
    block=True
)

@enable_keyban.handle()
async def _(event: GroupMessageEvent):
    self_id = check_self_id(event.self_id)
    switch_list[self_id].append(f'{event.group_id}')
    switch_list[self_id] = list(set(switch_list[self_id]))
    save_switch_list()
    await enable_keyban.finish('已启用关键词禁言服务')


disable_keyban = on_command(
    '/禁用keyban',
    aliases={'/关闭keyban'},
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN,
    priority=2,
    block=True
)

@disable_keyban.handle()
async def _(event: GroupMessageEvent):
    self_id = check_self_id(event.self_id)
    switch_list[self_id] = [i for i in switch_list[self_id] if not i == f'{event.group_id}']
    save_switch_list()
    await disable_keyban.finish('已禁用关键词禁言服务.')


keyword_ban = on_message(priority=90, block=False)

@keyword_ban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    self_id = check_self_id(event.self_id)

    if not f'{event.group_id}' in switch_list[self_id]:
        return

    loop = asyncio.get_running_loop()
    loop.create_task(get_ban(bot, event))


async def get_ban(bot: Bot, event: GroupMessageEvent) -> None:
    gid: int = event.group_id
    msg: str = event.get_plaintext()
    uid, flag = event.user_id, nm.flag if (nm := event.anonymous) else None
    ocr_text: list = []

    for i in event.get_message():
        try:
            if i.type == "image":
                text: list = await ocr_image(bot, i)
                ocr_text.append("\n".join(text))
        except ActionFailed as e:
            logger.debug(err_info(e))

    ban: list = []
    if msg:
        for i in kwd_db.execute(f'''
            select CONTENT, BAN_TIME from kwd_list
            where GROUP_ID={gid};
        '''.strip()):
            if re.search(i[0], msg):
                ban.append(i[1])

        for i in kwd_db.execute(f'''
            select CONTENT, BAN_TIME from regex_list
            where GROUP_ID={gid};
        '''.strip()):
            if re.search(i[0], msg):
                ban.append(i[1])

    for x in ocr_text:
        for i in string.whitespace:
            x = x.replace(i, x)
        if x:
            for i in kwd_db.execute(f'''
                select CONTENT, BAN_TIME from kwd_list
                where GROUP_ID={gid} and OCR=1;
            '''.strip()):
                if re.search(i[0], x):
                    ban.append(i[1])

            for i in kwd_db.execute(f'''
                select CONTENT, BAN_TIME from regex_list
                where GROUP_ID={gid} and OCR=1;
            '''.strip()):
                if re.search(i[0], x):
                    ban.append(i[1])

    ban_time: int = max(ban)

    if ban_time:
        await ban_user(bot, gid, [uid], ban_time, flag)


async def ocr_image(bot: Bot, i) -> list:
    await asyncio.sleep(random()+0.5)
    text: list = []
    text_list: list = (await bot.ocr_image(image=str(i.data["file"])))["texts"]
    for j in text_list:
        text.append(j["text"])
    return text


async def see_list(
    table: Literal["kwd_list", "regex_list"],
    bot: Bot,
    event: GroupMessageEvent
) -> str | None:
    node: list = []
    for i in kwd_db.execute(f'''
        select CONTENT, OCR, BAN_TIME from {table}
        where GROUP_ID={event.group_id};
    '''.strip()):
        node.append({
            "type": "node",
            "data": {
                "name": event.sender.card or event.sender.nickname or '老色批',
                "uin": event.user_id,
                "content": (
                    f"内容: {i[0]}\n"
                    f"OCR: {True if i[1] else False}\n"
                    f"禁言时间: {i[2]}秒"
                )
            }
        })

    if not node:
        return "列表为空."

    await bot.send_group_forward_msg(group_id=event.group_id, messages=node)


def handle_msg(
    table: Literal["kwd_list", "regex_list"],
    mode: bool,
    gid: int,
    arg: Message = CommandArg(),
) -> str:

    _help: str = "发送 /keyban 查看帮助"

    if not (args := arg.extract_plain_text().split("\n")):
        return _help

    ban_time: int = (
        3600
        if not re.search(
            r'^[1-9]\d*((个|個|箇)?(月|小?(时|時))|(天|日)|分|秒)?', args[0]
        )
        else b_time(Message(args.pop(0)))
    ) if mode else 0

    if not args:
        return _help

    ocr: bool = False
    if args[0].lower() == "ocr":
        ocr = True
        args.pop(0)

    if not args:
        return _help

    for i in args:
        if not i.strip():
            continue
        handle_db(table, mode, gid, i.strip(), ocr, ban_time)

    return "我记住了~" if mode else "已删除."


def handle_db(
    table: Literal["kwd_list", "regex_list"],
    mode: bool,
    gid: int,
    msg: str,
    ocr: bool,
    ban_time: int,
) -> None:
    if mode:
        if [ i[0] for i in kwd_db.execute(f'''
            select BAN_TIME from {table}
            where GROUP_ID={gid} and CONTENT='{msg}';
        ''') ]:
            kwd_db.execute(f'''
                update {table} set OCR={ocr}, BAN_TIME={ban_time}
                where GROUP_ID={gid} and CONTENT='{msg}';
            '''.strip())
        else:
            kwd_db.execute(f'''
                insert into {table}(GROUP_ID, CONTENT, OCR, BAN_TIME)
                values({gid}, '{msg}', {ocr}, {ban_time});
            '''.strip())
    else:
        kwd_db.execute(f'''
            delete from {table} where GROUP_ID={gid} and CONTENT='{msg}';
        '''.strip())
    kwd_db.commit()

