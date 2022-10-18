from nonebot import on_metaevent
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    LifecycleMetaEvent
)
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from pathlib import Path



bot_info = Path(".") / "bot_id.json"

async def check_first_connect(_: LifecycleMetaEvent) -> bool:
    return True

start_metaevent = on_metaevent(rule=check_first_connect, temp=True)
@start_metaevent.handle()
async def start(bot: Bot) -> None:
    user_id = await bot.get_login_info()
    user_id = json.dumps(user_id)
    with open(bot_info,"w+",encoding="utf-8") as g:
        g.write(str(user_id))
        g.close()

    for superuser in bot.config.superusers:
        await bot.send_private_msg(user_id=int(superuser), message=Message("Bot启动成功"))
