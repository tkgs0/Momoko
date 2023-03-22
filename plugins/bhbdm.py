from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import on_command
from urllib.parse import quote
import base64 as b64



url = [
    'https://www.google.com/search?lr=lang_zh-CN%7Clang_zh-TW&q=',
    'https://yandex.com/search/?text=',
    'https://baidu.ma/?q='
]
    


to_gg = on_command("/谷歌搜索", priority=5, block=True)

@to_gg.handle()
async def _(arg: Message = CommandArg()):
    await to_gg.finish(url[0] + quote(arg.extract_plain_text()))



to_ydx = on_command("/毛哥搜索", priority=5, block=True)

@to_ydx.handle()
async def _(arg: Message = CommandArg()):
    await to_ydx.finish(url[1] + quote(arg.extract_plain_text()))



bhbdm = on_command("/百度搜索", priority=5, block=True)

@bhbdm.handle()
async def _(arg: Message = CommandArg()):
    await bhbdm.finish(url[2] + b64.b64encode(arg.extract_plain_text().encode()).decode())
