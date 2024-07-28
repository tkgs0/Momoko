from nonebot import on_command, on_message, on_notice
from nonebot.rule import Rule, to_me
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    PokeNotifyEvent,
    MessageSegment
)
import ujson as json
from pathlib import Path
import asyncio, random
from .utils import (
    # Bot_NICKNAME,
    MODE_LIST,
    hello__reply,
    get_chat_result
)


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


def poke_to_me(event: PokeNotifyEvent) -> bool:
    return event.self_id == event.target_id


poke_ = on_notice(rule=Rule(poke_to_me), priority=999, block=False)

@poke_.handle()
async def _(event: PokeNotifyEvent):
    if not random.random()*10//1%6:
        await asyncio.sleep(random.random()+1)
        # await poke_.finish(f'请不要戳{Bot_NICKNAME}>_<')
        await poke_.finish(MessageSegment('poke', {'qq': event.user_id}))


ai = on_message(rule=to_me(), priority=999, block=False)

@ai.handle()
async def _(event: MessageEvent):
    # 获取纯文本消息
    msg = event.get_plaintext().strip()

    result = (
        random.choice(hello__reply)
        if not msg or msg in [
            '你好啊',
            '你好',
            '在吗',
            '在不在',
            '您好',
            '您好啊',
            '你好',
            '在'
        ] else None
    ) or (
        await get_chat_result(
            conf['mode'],
            msg,
            f'{event.self_id}{event.user_id}'
        )
    )

    # matcher.stop_propagation()

    await asyncio.sleep(random.random()*2+2)

    try:
        await ai.send(Message(result))
    except Exception:
        await ai.finish('ʕ  •ᴥ•ʔ<Err>')


'''
小爱语音回复需在 .env 添加 XIAOAI_VOICE=true
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
    if msg:
        try:
            conf['mode'] = MODE_LIST.index(msg[:2])
        except ValueError:
            await set_reply.finish('模式不存在.')
    else:
        conf['mode'] = (conf['mode'] + 1) % len(MODE_LIST)
    save_conf()
    await set_reply.finish(f"已设置回复模式{MODE_LIST[conf['mode']]}")

