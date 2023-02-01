import re, time, random
from nonebot import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
    ActionFailed,
)


flmt_notice = random.choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])


def err_info(e: ActionFailed):
    if e1 := e.info.get('wording'):
        return e1
    elif e1 := e.info.get('msg'):
        return e1
    else:
        return repr(e)


def format_time(_time: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_time))


async def ban_user(
    bot: Bot,
    gid: int,
    userlist: list[int] = [],
    _time: int = 43200,
    nmflag = None
) -> str | None:
    x = True
    try:
        if nmflag:
            await bot.set_group_anonymous_ban(
                group_id=gid,
                anonymous_flag=nmflag,
                duration=_time
            )
            return
        if not userlist:
            logger.warning('未指定要禁言的用户!')
            return
        for user in userlist:
            await bot.set_group_ban(
                user_id=user,
                group_id=gid,
                duration=_time
            )
    except Exception as e:
        logger.warning(repr(e))
        x = None
    return x if not x else '设置成功~'


def ban_time(arg: Message = CommandArg()) -> int:
    try:
        _time = arg.extract_plain_text().strip()
        _time = re.search(r'[1-9]\d*(天|小?(时|時)|分)?', _time).group()  # type: ignore
        time1 = re.match(r'\d*', _time).group()  # type: ignore
        time2 = _time.replace(time1, '')
        time1 = int(time1)
        if '时' in time2 or '時' in time2:
            time3 = time1*60*60
        elif '天' in time2:
            time3 = time1*60*60*24
        else:
            time3 = time1*60
        return time3 if time3 <= 2591940 else 2591940
    except:
        return 43200


async def setwholeban(
    enable: bool,
    bot: Bot,
    event: MessageEvent,
    arg: Message = CommandArg(),
):
    gids = arg.extract_plain_text().strip().split()
    if not gids:
        if isinstance(event, GroupMessageEvent):
            gids.append(f'{event.group_id}')
        else:
            return '用法: \n开启(关闭)全员禁言 群 群1 群2 ...'
    for gid in gids:
        if not is_number(gid):
            return '参数错误, 群号必须是数字..'
    x = True
    try:
        for gid in gids:
            await bot.set_group_whole_ban(group_id=int(gid), enable=enable)
    except Exception as e:
        logger.warning(repr(e))
        x = None
    return x if not x else True


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
