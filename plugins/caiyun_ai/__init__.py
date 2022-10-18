import re
from typing import List, Union
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot import on_command, require
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    Message,
    MessageSegment,
)

require("nonebot_plugin_imageutils")
from nonebot_plugin_imageutils import text2image, BuildImage

from .config import Config
from .data_source import CaiyunAi, model_list

__plugin_meta__ = PluginMetadata(
    name="彩云小梦",
    description="彩云小梦AI续写",
    usage="@我 续写 xxx",
    config=Config,
    extra={
        "unique_name": "caiyunai",
        "example": "@小Q 续写 小Q是什么",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.2.5",
    },
)


novel = on_command("续写", aliases={"彩云小梦"}, block=True, rule=to_me(), priority=12)


@novel.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    content = msg.extract_plain_text().strip()
    if content:
        matcher.set_arg("content", msg)


@novel.got("content", prompt="请发送要续写的内容")
async def _(matcher: Matcher, state: T_State, content: str = ArgPlainText()):
    matcher.set_arg("reply", Message(f"续写{content}"))
    caiyunai = CaiyunAi()
    state["caiyunai"] = caiyunai


@novel.got("reply")
async def _(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    reply: str = ArgPlainText(),
):
    caiyunai: CaiyunAi = state["caiyunai"]

    match_continue = re.match(r"续写\s*(\S+.*)", reply, re.S)
    match_select = re.match(r"选择分支\s*(\d+)", reply)
    match_model = re.match(r"切换模型\s*(\S+)", reply)
    match_stop = re.match(r"结束|停|stop", reply)

    model_help = f"支持的模型：{'、'.join(list(model_list))}"
    if match_model:
        model = match_model.group(1).strip()
        if model not in model_list:
            await novel.reject(model_help)
        else:
            caiyunai.model = model
            await novel.reject(f"模型已切换为：{model}")
    elif match_continue:
        content = match_continue.group(1)
        caiyunai.content = content
    elif match_select:
        num = int(match_select.group(1))
        if num < 1 or num > len(caiyunai.contents):
            await novel.reject("请发送正确的编号")
        caiyunai.select(num - 1)
    elif match_stop:
        await novel.finish("续写已结束")
    else:
        await novel.reject()

    await novel.send("loading...")
    err_msg = await caiyunai.next()
    if err_msg:
        await novel.finish(f"出错了：{err_msg}")

    msgs = []
    nickname = model_list[caiyunai.model]["name"]
    help_msg = (
        "发送“选择分支 编号”选择分支\n"
        "发送“续写 内容”手动添加内容\n"
        "发送“切换模型 名称”切换模型\n"
        f"{model_help}\n"
        "发送“结束”结束续写"
    )
    msgs.append(help_msg)
    result = BuildImage(
        text2image(caiyunai.result, padding=(20, 20), max_width=800)
    ).save_jpg()
    msgs.append(MessageSegment.image(result))
    for i, content in enumerate(caiyunai.contents, start=1):
        msgs.append(f"{i}、\n{content}")
    try:
        await send_forward_msg(bot, event, nickname, bot.self_id, msgs)
    except:
        await novel.finish("消息发送失败，续写结束")
    await novel.reject()


async def send_forward_msg(
    bot: Bot,
    event: MessageEvent,
    name: str,
    uin: str,
    msgs: List[Union[str, MessageSegment]],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )
