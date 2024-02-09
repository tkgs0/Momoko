import asyncio, random
from nonebot import on_command, logger
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, ActionFailed


usage:str = """

指令表:
    (私聊广播)
    pbc 广播内容

    (群聊广播)
    gbc 广播内容

示例:
    gbc 我xx很大, 请偷偷x我

""".strip()


__plugin_meta__ = PluginMetadata(
    name="广播",
    description="遍历好友/群聊列表发送消息",
    usage=usage,
    type="application"
)


group_broadcast = on_command(
    "gbc",
    aliases={"群聊广播"},
    permission=SUPERUSER,
    priority=5,
    block=True
)

@group_broadcast.handle()
async def _(matcher: Matcher, args: Message = CommandArg()) -> None:
    if args:
        matcher.state["content"] = Message(args)


@group_broadcast.got("content", "内容呢?")
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    msg = matcher.state["content"]
    group_list = await bot.get_group_list()
    await group_broadcast.send(f"正在发送...\n共{len(group_list)}个群聊, 预计需要{len(group_list) * 8.0 / 60}分钟.")
    err = {}
    for group in group_list:
        await asyncio.sleep(random.random() * 10 / 2 + 5)
        try:
            await bot.send_group_msg(group_id=group["group_id"], message=Message(msg))
        except ActionFailed as e:
            logger.error(repr(e))
            e1 = err_info(e)
            if err.get(e1):
                err["e1"].append(group["group_id"])
            else:
                err.update({
                    e1: [group["group_id"]]
                })
    if err:
        err_msg = "\n\n".join([f"{k}\n{err.get(k)}" for k in err])
        await bot.send_private_msg(user_id=event.user_id, message=f"群聊广播发送失败:\n\n{err_msg}")
    await group_broadcast.finish(f"已完成. {len(err)}个失败.")


private_broadcast = on_command(
    "pbc",
    aliases={"私聊广播"},
    permission=SUPERUSER,
    priority=5,
    block=True
)


@private_broadcast.handle()
async def _(matcher: Matcher, args: Message = CommandArg()) -> None:
    if args:
        matcher.state["content"] = Message(args)


@private_broadcast.got("content", "内容呢?")
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    msg = matcher.state["content"]
    friend_list = await bot.get_friend_list()
    await private_broadcast.send(f"正在发送...\n共{len(friend_list)}个好友, 预计需要{len(friend_list) * 8.0 / 60}分钟.")
    err = {}
    for user in friend_list:
        await asyncio.sleep(random.random() * 10 / 2 + 5)
        try:
            await bot.send_private_msg(user_id=user["user_id"], message=Message(msg))
        except ActionFailed as e:
            logger.error(repr(e))
            e1 = err_info(e)
            if err.get(e1):
                err["e1"].append(user["user_id"])
            else:
                err.update({
                    e1: [user["user_id"]]
                })
    if err:
        err_msg = "\n\n".join([f"{k}\n{err.get(k)}" for k in err])
        await bot.send_private_msg(user_id=event.user_id, message=f"私聊广播发送失败:\n\n{err_msg}")
    await private_broadcast.finish(f"已完成. {len(err)}个失败.")


def err_info(e: ActionFailed) -> str:
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)
