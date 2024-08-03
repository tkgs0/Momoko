from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    MessageEvent,
    ActionFailed
)
from nonebot.adapters.onebot.v11.helpers import Cooldown

from .utils import edit_img


usage: str = """

指令表:
    应援 xxx

""".strip()


__plugin_meta__ = PluginMetadata(
    name="应援",
    description="熊猫头举牌",
    usage=usage,
    type="application"
)


def err_info(e: ActionFailed) -> str:
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)


ouen = on_command(
    '应援',
    aliases={'應援', '応援'},
    priority=5,
    block=False
)


@ouen.handle([Cooldown(30, prompt='慢...慢一..点❤')])
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    text = f"{args}"
    if uids := [at.data['qq'] for at in event.get_message()['at']]:
        for i in uids:
            info = await bot.get_stranger_info(user_id=i, no_cache=True)
            text = text.replace(f"[CQ:at,qq={i}]", info['nickname'])
    try:
        await ouen.finish(Message(MessageSegment.image(edit_img(text.strip()), cache=False)))
    except ActionFailed as e:
        logger.error(e)
        await ouen.finish(err_info(e))
