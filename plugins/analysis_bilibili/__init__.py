import re
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.log import logger
from .analysis_bilibili import config, b23_extract, bili_keyword

analysis_bili = on_regex(
    r"(b23.tv)|(bili(22|23|33|2233).cn)|(.bilibili.com)|(^(av|cv)(\d+))|(^BV([a-zA-Z0-9]{10})+)|"
    r"(\[\[QQ小程序\]哔哩哔哩\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)",
    flags=re.I,
)

blacklist = getattr(config, "analysis_blacklist", [])
group_blacklist = getattr(config, "analysis_group_blacklist", [])


@analysis_bili.handle()
async def analysis_main(event: MessageEvent) -> None:
    text = str(event.message).strip()
    if blacklist and int(event.get_user_id()) in blacklist:
        return
    if re.search(r"(b23.tv)|(bili(22|23|33|2233).cn)", text, re.I):
        # 提前处理短链接，避免解析到其他的
        text = await b23_extract(text)
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
    else:
        group_id = None
    if group_id in group_blacklist:
        return
    msg = await bili_keyword(group_id, text)
    if msg:
        try:
            msg = re.sub(r"简介(.|\s)*", "", str(msg))
            await analysis_bili.send(msg)
        except Exception as e:
            logger.exception(e)
