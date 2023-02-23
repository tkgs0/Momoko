from nonebot import get_driver, on_command, on_message, on_notice
from nonebot.rule import to_me
from nonebot.params import CommandArg, ArgStr
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    PokeNotifyEvent,
    MessageSegment
)
from nonebot.adapters.onebot.v11.helpers import (
    Cooldown,
    CooldownIsolateLevel
)
import ujson as json
from pathlib import Path
import asyncio, random
from .utils import (
    # Bot_NICKNAME,
    hello__reply,
    get_chat_result,
    xiaosi,
    xiaoai
)

from . import gpt


confpath: Path = Path() / 'data' / 'smart_reply' / 'reply.json'
confpath.parent.mkdir(parents=True, exist_ok=True)

default_conf: dict = {'mode': 0}
conf: dict = (
    json.loads(confpath.read_text('utf-8'))
    if confpath.is_file() else default_conf
)
conf: dict = conf if conf.keys() == default_conf.keys() else default_conf


def save_conf() -> None:
    confpath.write_text(json.dumps(conf), encoding='utf-8')


poke_ = on_notice(priority=99, block=False)

@poke_.handle()
async def _(event: PokeNotifyEvent):
    if event.self_id == event.target_id:
        await asyncio.sleep(random.random()+1)
        # await poke_.finish(f'请不要戳{Bot_NICKNAME}>_<')
        await poke_.finish(MessageSegment('poke', {'qq': event.user_id}))


ai = on_message(rule=to_me(), priority=99, block=False)

@ai.handle()
async def _(event: MessageEvent):

    if conf['mode'] == 1:
        get_reply = xiaoai
    elif not conf['mode']:
        get_reply = xiaosi
    else:
        return

    # 获取纯文本消息
    msg = event.get_plaintext()

    await asyncio.sleep(random.random()*2+1)

    msg = msg.strip()
    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
    if not msg or msg in [
        '你好啊',
        '你好',
        '在吗',
        '在不在',
        '您好',
        '您好啊',
        '你好',
        '在',
    ]:
        await ai.finish(Message(random.choice(hello__reply)))
    # 从字典里获取结果
    result = await get_chat_result(msg)
    # 如果词库没有结果，则调用对话api获取回复
    if not result:
        result = await get_reply(msg)
    await ai.finish(Message(result))

_flmt_notice = random.choice([
    "慢...慢一..点❤",
    "要坏...坏掉惹❤",
    "等..等一...下❤",
    "冷静1下",
])
@ai.handle([Cooldown(
    60,
    prompt=_flmt_notice,
    isolate_level=CooldownIsolateLevel.GLOBAL
)])
async def _(event: MessageEvent):
    if not conf['mode'] == 2:
        return
    msg = event.get_plaintext().strip()
    await ai.finish(Message(
        gpt.get_chat(msg, str(event.user_id))
        if msg else 'ʕ  •ᴥ•ʔ ?'
    ), at_sender=True)


'''
小爱语音回复需在 .env 添加 XIAOAI_VOICE=true

ChatGPT回复需在 .env 添加openai帐号和密码
⚠注意: 插件会将openai帐密上传到**第三方API**过`人机验证`来获取令牌
  CHATGPT_USR="xxxxx"
  CHATGPT_PWD="xxxxx"
'''
set_reply = on_command(
    '设置回复模式',
    aliases={'切换回复模式'},
    permission=SUPERUSER,
    priority=2,
    block=True
)

@set_reply.handle()
async def _(arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if msg.startswith('思知') or msg.startswith('小思'):
        conf['mode'] = 0
    elif msg.startswith('小爱'):
        conf['mode'] = 1
    elif msg.lower().startswith('gpt') or msg.lower().startswith('chatgpt'):
        conf['mode'] = 2
    elif not msg:
        conf['mode'] = conf['mode'] + 1 if conf['mode'] < 2 else 0
    else:
        await set_reply.finish('模式不存在.')
    save_conf()
    mode = ['小思', '小爱', 'ChatGPT']
    await set_reply.finish(f'已设置回复模式{mode[conf["mode"]]}')


clear_all_chat = on_command(
    '清空对话列表',
    rule=to_me(),
    permission=SUPERUSER,
    priority=2,
    block=True
)

@clear_all_chat.got('flag', prompt='确定吗? (Y/n)')
async def _(flag: str = ArgStr('flag')):
    if flag.lower().strip() in ['y', 'yes', 'true']:
        msg = gpt.clear_all_chat()
        await clear_all_chat.finish(msg if msg else '已清空对话列表.')
    await clear_all_chat.finish('操作已取消.')


clear_chat = on_command(
    '重置对话',
    rule=to_me(),
    priority=15,
    block=True
)

@clear_chat.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    uids = None
    res = None
    if str(event.user_id) in get_driver().config.superusers:
        uids = [at.data['qq'] for at in event.get_message()['at']]
        if not uids:
            uids = handle_msg(arg)
    if uids:
        for i in uids:
            if res := gpt.clear_chat(i):
                break
    else:
        res = gpt.clear_chat(str(event.user_id))
    await clear_chat.finish(res if res else '对话已重置.')


def handle_msg(arg) -> list | str:
    uids = arg.extract_plain_text().strip().split()
    for uid in uids:
        if not is_number(uid):
            return '参数错误, qq号必须是数字..'
    return uids


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

