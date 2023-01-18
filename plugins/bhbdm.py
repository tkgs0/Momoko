from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import on_command
from urllib.parse import quote



def run(msg: str, x: str) -> str:
    _engine = {
        'google': 'https://www.google.com/search?lr=lang_zh-CN%7Clang_zh-TW&q=',
        'yandex': 'https://yandex.com/search/?text=',
        'baidu': 'https://buhuibaidu.me/?s='
    }
    msg = _engine[x] + quote(msg)
    return msg



to_gg = on_command("/谷歌搜索", priority=5, block=True)

@to_gg.handle()
async def _(message: Message = CommandArg()):
    url = run(str(message), 'google')
    await to_gg.finish(url)



to_ydx = on_command("/毛哥搜索", priority=5, block=True)

@to_ydx.handle()
async def _(message: Message = CommandArg()):
    url = run(str(message), 'yandex')
    await to_ydx.finish(url)



bhbdm = on_command("/百度搜索", priority=5, block=True)

@bhbdm.handle()
async def _(message: Message = CommandArg()):
    url = run(str(message), 'baidu')
    await bhbdm.finish(url)
