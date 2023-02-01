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



bot_info = Path() / "data" / "bot_id.json"
bot_info.parent.mkdir(parents=True, exist_ok=True)

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
    
    superusers = bot.config.superusers

    gl = await bot.get_friend_list()
    friends = ["{user_id}".format_map(g) for g in gl]
    for superuser in superusers:
        if not superuser in friends:
            raise KeyboardInterrupt("\033[40;33;1m存在非bot好友的超级用户, 请先添加Bot为好友!\033[0m")

    for superuser in superusers:
        await bot.send_private_msg(
            user_id=int(superuser),
            message=Message("Bot启动成功")
        )

