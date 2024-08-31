import re
from typing import Union
from nonebot.adapters.onebot.v11 import Message, MessageSegment, escape


def msg_checker(message: Union[Message, dict, str]) -> Message | str:
    if isinstance(message, str):
        return message if check_cq_code(message) else escape(message)

    cache_list = []
    for i in message:
        _type = i.get("type")
        _data = i.get("data")
        if _type == "text":
            if check_cq_code(_data["text"]):
                cache_list.append(_data["text"])
            else:
                cache_list.append(escape(_data["text"]))
        elif _type == "image":
            file, url = _data.get("file"), _data.get("url")
            check = check_image_url(file, url)
            if check:
                cache_list.append(MessageSegment.image(url or file))
            else:
                cache_list.append(f"[图片风险, file: {file}, url: {url}]")
        elif _type == "face":
            cache_list.append(MessageSegment.face(_data["id"]))
        else:
            cache_list.append(f"[�: {_data}]")

    return "".join(map(str, cache_list))


tenc_gchat_url: str = r"https?://[^\.\/]+\.qpic\.cn/"
may_inject_keys: list = ["record", "video", "music", "xml", "json"]
"""
检查所传回的信息是否被注入
"""
def check_cq_code(text: str) -> bool:
    _type = re.findall(r"CQ:(.*?),", text, re.I)
    for i in _type:
        if i == "image":
            if (t := re.findall(r"file=(.*?)[,\]]", text, re.I)) and re.match(r"[A-z0-9]+://", t[0], re.I):
                return False
            if (t := re.findall(r"url=(.*?)[,\]]", text, re.I)) and not re.match(tenc_gchat_url, t[0], re.I):
                return False
        if i in may_inject_keys:
            return False
    return True


def check_image_url(file, url) -> bool:
    if re.match(r"[A-z0-9]+://", file, re.I):
        return False
    if url and not re.match(tenc_gchat_url, url, re.I):
        return False
    return True
