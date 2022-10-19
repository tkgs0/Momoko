from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import on_command
from nonebot.permission import SUPERUSER



echo = on_command("：", to_me(), priority=5, block=True, permission=SUPERUSER)

@echo.handle()
async def echo_escape(message: Message = CommandArg()):
    await echo.finish(message=message)



_snapshot = on_command("/快照", priority=5, block=True, permission=SUPERUSER)

@_snapshot.handle()
async def _(message: Message = CommandArg()):
    url = str(message)
    try:
        await _snapshot.send(MessageSegment.image(f"https://image.thum.io/get/width/1280/crop/1440/viewportWidth/1280/png/noanimate/{url}"))
    except Exception as e:
        await _snapshot.finish(repr(e))
