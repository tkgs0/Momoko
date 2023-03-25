import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageEvent,
    ActionFailed,
)
from nonebot.log import logger

from .analysis_bilibili import B23_REGEX, b23_extract, bili_keyword
from .config import config

DESC_REGEX = re.compile(r"\s*简介(.|\s)*")
analysis_bili = on_regex(
    r"(b23.tv)|(bili(22|23|33|2233).cn)|(.bilibili.com)|(^(av|cv)(\d+))|(^BV([a-zA-Z0-9]{10})+)|"
    r"(\[\[QQ小程序\]哔哩哔哩\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)",
    flags=re.I,
)


@analysis_bili.handle()
async def analysis_main(event: MessageEvent) -> None:
    text = str(event.message).strip()
    if event.sender.user_id in config.analysis_blacklist:
        return
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
        if group_id in config.analysis_group_blacklist:
            return
    else:
        group_id = None
    if B23_REGEX.search(text):
        # 提前处理短链接，避免解析到其他的
        text = await b23_extract(text)
    msg = await bili_keyword(group_id, text)
    if msg:
        try:
            msg = re.sub(DESC_REGEX, "", str(msg))
            await analysis_bili.send(msg)
        except ActionFailed as e:
            logger.warning(err_info(e))
        except Exception as e:
            logger.exception(e)


def err_info(e: ActionFailed) -> str:
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)
