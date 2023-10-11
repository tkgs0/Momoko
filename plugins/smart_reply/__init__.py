from nonebot import on_command, on_message, on_notice
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    PokeNotifyEvent,
    MessageSegment
)
from nonebot.adapters.onebot.v11.helpers import Cooldown
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

try:
    from ..mockingbird import get__voice
except Exception:
    get__voice = None


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


poke_ = on_notice(priority=999, block=False)

@poke_.handle([Cooldown(10)])
async def _(event: PokeNotifyEvent):
    if event.self_id == event.target_id:
        await asyncio.sleep(random.random()+1)
        # await poke_.finish(f'请不要戳{Bot_NICKNAME}>_<')
        await poke_.finish(MessageSegment('poke', {'qq': event.user_id}))


ai = on_message(rule=to_me(), priority=999, block=False)

@ai.handle()
async def _(state: T_State, event: MessageEvent, matcher: Matcher):
    # 获取纯文本消息
    msg = event.get_plaintext().strip()

    if conf['mode'] == 1:
        get_reply = xiaoai
    else:
        get_reply = xiaosi

    await asyncio.sleep(random.random()*2+1)

    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
    result = (
        random.choice(hello__reply)
        if not msg or msg in [
            '你好啊', '你好', '在吗', '在不在', '您好', '您好啊', '你好', '在']
        else None
    ) or (await get_chat_result(msg)) or (await get_reply(msg))
    # 从字典里获取结果
    # 如果词库没有结果，则调用对话api获取回复

    # matcher.stop_propagation()

    await ai.send(Message(result))

    if get__voice and isinstance(result, str) and not result.startswith('ʕ  •ᴥ•ʔ'):
            await get__voice(matcher, state, result)


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
    if msg.startswith('思知') or msg.startswith('小思'):
        conf['mode'] = 0
    elif msg.startswith('小爱'):
        conf['mode'] = 1
    elif not msg:
        conf['mode'] = 0 if conf['mode'] else 1
    else:
        await set_reply.finish('模式不存在.')
    save_conf()
    mode = ['小思', '小爱']
    await set_reply.finish(f'已设置回复模式{mode[conf["mode"]]}')

