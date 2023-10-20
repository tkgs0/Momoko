from nonebot import on_metaevent
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    LifecycleMetaEvent
)


async def check_first_connect(_: LifecycleMetaEvent) -> bool:
    return True

start_metaevent = on_metaevent(rule=check_first_connect, temp=True)
@start_metaevent.handle()
async def start(bot: Bot) -> None:
    bot_info = await bot.get_login_info()
    
    superusers = bot.config.superusers

    gl = await bot.get_friend_list()
    friends = ["{user_id}".format_map(g) for g in gl]
    for superuser in superusers:
        if not superuser in friends:
            raise KeyboardInterrupt(f"\n\033[40;33;1mBot: {bot_info['user_id']}\n存在非bot好友的超级用户 {superuser}, 请先添加Bot为好友!\033[0m")

    for superuser in superusers:
        await bot.send_private_msg(
            user_id=int(superuser),
            message=Message("Bot启动成功")
        )

