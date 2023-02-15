from nonebot.plugin.on import on_command, on_message, on_notice
from nonebot.rule import to_me
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
import asyncio, random  # , string
from .utils import (
    # Bot_NICKNAME,
    hello__reply,
    get_chat_result,
    xiaosi,
    xiaoai
)

confpath = Path() / 'data' / 'smart_reply' / 'reply.json'
confpath.parent.mkdir(parents=True, exist_ok=True)

conf = (
    json.loads(confpath.read_text('utf-8'))
    if confpath.is_file()
    else {'xiaoai': False}
)


def save_conf():
    confpath.write_text(json.dumps(conf), encoding='utf-8')


poke_ = on_notice(priority=99, block=False)

@poke_.handle()
async def _(event: PokeNotifyEvent):
    if event.self_id == event.target_id:
        await asyncio.sleep(random.random()+1)
        # await poke_.finish(f'请不要戳{Bot_NICKNAME}>_<')
        await poke_.finish(MessageSegment('poke', {'qq': event.user_id}))



# 优先级99, 条件: 艾特bot就触发
ai = on_message(rule=to_me(), priority=99,block=False)

@ai.handle()
async def _(event: MessageEvent):

    get_reply = xiaoai if conf['xiaoai'] else xiaosi

    # 获取纯文本消息
    msg = event.get_plaintext()

    await asyncio.sleep(random.random()*2+1)

    # for i in string.punctuation:
    #     msg = msg.replace(i, ' ')

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


# 小爱语音回复需在 .env 添加 XIAOAI_VOICE=true
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
        conf['xiaoai'] = False
    elif msg.startswith('小爱'):
        conf['xiaoai'] = True
    elif not msg:
        conf['xiaoai'] = not conf['xiaoai']
    else:
        await set_reply.finish('模式不存在.')
    save_conf()
    await set_reply.finish(f'已设置回复模式{"小爱" if conf["xiaoai"] else "小思"}')
