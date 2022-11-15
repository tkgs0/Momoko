from nonebot.plugin.on import on_message, on_notice
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    PokeNotifyEvent,
    MessageSegment,
)
from .utils import *



poke_ = on_notice(priority=99, block=False)

@poke_.handle()
async def _(event: PokeNotifyEvent):
    if event.self_id == event.target_id:
        # await poke_.finish(f"请不要戳{Bot_NICKNAME}>_<")
        await poke_.finish(MessageSegment("poke", {"qq": event.user_id}))




# 优先级99, 条件: 艾特bot就触发
ai = on_message(rule=to_me(), priority=99,block=False)

@ai.handle()
async def _(event: MessageEvent):
    # 获取消息文本
    msg = str(event.get_message())
    # 去掉带中括号的内容(去除cq码)
    msg = re.sub(r"\[.*?\]", "", msg)
    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
    if (not msg) or msg.isspace() or msg in [
        "你好啊",
        "你好",
        "在吗",
        "在不在",
        "您好",
        "您好啊",
        "你好",
        "在",
    ]:
        await ai.finish(Message(random.choice(hello__reply)))
    # 从字典里获取结果
    result = await get_chat_result(msg)
    # 如果词库没有结果，则调用ownthink获取智能回复
    if result == None:
        url = f"https://api.ownthink.com/bot?appid=xiaosi&userid=user&spoken={msg}"
        message = await get_reply(url)
        await ai.finish(message=message)
    await ai.finish(Message(result))
