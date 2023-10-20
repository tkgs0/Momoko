from nonebot import on_metaevent
from nonebot.adapters.onebot.v11 import (
    Bot,
    LifecycleMetaEvent
)


async def check_first_connect(_: LifecycleMetaEvent) -> bool:
    return True

start_metaevent = on_metaevent(rule=check_first_connect, temp=True)
@start_metaevent.handle()
async def _(bot: Bot) -> None:
    bot_info = await bot.get_login_info()
    
    superusers = bot.config.superusers

    gl = await bot.get_friend_list()
    friends = ["{user_id}".format_map(g) for g in gl]
    for superuser in superusers:
        if not superuser in friends:
            raise KeyboardInterrupt(f"\033[40;33;1m存在非 Bot {bot_info['user_id']} 好友的超级用户 {superuser}, 请先添加Bot为好友!\033[0m")

    for superuser in superusers:
        await bot.send_private_msg(
            user_id=int(superuser),
            message="Bot启动成功"
        )

