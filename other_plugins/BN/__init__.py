import asyncio, time, re, unicodedata
from pathlib import Path
import ujson as json
from binance.spot import Spot
from binance.error import ClientError
from nonebot import (
    on_metaevent,
    on_command,
    on_regex,
    logger,
    get_bot,
    get_plugin_config,
    require
)
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    MessageEvent,
    GroupMessageEvent,
    LifecycleMetaEvent,
    ActionFailed,
    GROUP_ADMIN,
    GROUP_OWNER
)
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .config import Config


"""
cron 格式

* * * * *
秒 分 时 日 月

month (1-12)

day of month (1-31)

hour (0-23)

minute (0-59)

second (0-59)

"""


usage: str = """

指令表:
    xxx/xxx  # 查询
    添加BN推送 xxx/xxx
    删除BN推送 xxx/xxx

""".strip()


__plugin_meta__ = PluginMetadata(
    name="BN",
    description="BN查询",
    usage=usage,
    type="application"
)


confpath = Path() / "data" / "BN" / "config.json"
confpath.parent.mkdir(parents=True, exist_ok=True)

enabled = (
    json.loads(confpath.read_text('utf-8'))
    if confpath.is_file()
    else {}
)


account = get_plugin_config(Config)
client = (
    Spot(account.binance_key, account.binance_secret_key)
    if account.binance_key and account.binance_secret_key
    else Spot()
)


def check_first_connect(_: LifecycleMetaEvent) -> bool:
    return True

@on_metaevent(rule=check_first_connect, temp=True).handle()
async def _():
    if not scheduler.running:
        try:
            scheduler.start()
            logger.success("scheduler已启动.")
        except Exception as e:
            logger.error(f"scheduler启动失败!\n{repr(e)}")


def save_config() -> None:
    confpath.write_text(json.dumps(enabled), encoding='utf-8')


def err_info(e: ActionFailed) -> str:
    logger.error(repr(e))
    e1 = 'Failed: '
    if e2 := e.info.get('wording'):
        return e1 + e2
    elif e2 := e.info.get('msg'):
        return e1 + e2
    else:
        return repr(e)


def check_self_id(self_id) -> str:
    self_id = f'{self_id}'
    if not enabled.get(self_id):
        enabled.update({
            self_id: {}
        })
    save_config()
    return self_id


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def handle_enabled(
    self_id,
    uid: str,
    mode: bool,
    args: Message,
) -> str:
    self_id = check_self_id(self_id)
    text = args.extract_plain_text().upper()

    if mode:
        try:
            a, b = text.split("/")
            if a == b:
                return "1:1"
            symbol = a + b
        except Exception:
            return "格式错误."
        try:
            res: str = client.ticker_price(symbol)["price"]
        except ClientError as e:
            logger.debug(err := e.error_message)
            return err
        if arg := enabled[self_id].get(uid):
            arg.append(text)
            enabled[self_id][uid] = list(set(arg))
        else:
            enabled[self_id].update({uid: [text]})

        msg = f"已添加, 当前值: {res}"
    else:
        if arg := enabled[self_id].get(uid):
            enabled[self_id][uid] = [i for i in arg if i != text]
        else:
            enabled[self_id].update({uid: []})
        msg = "已删除."

    save_config()
    return msg


enable_bn = on_command(
    "添加BN推送",
    permission=SUPERUSER|GROUP_OWNER|GROUP_ADMIN,
    priority=2,
    block=True
)

@enable_bn.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not args:
        await enable_bn.finish("需要参数.")
    msg = handle_enabled(event.self_id, f'{event.group_id}', True, args)
    await enable_bn.finish(msg, reply_message=True)


disable_bn = on_command(
    "删除BN推送",
    permission=SUPERUSER|GROUP_OWNER|GROUP_ADMIN,
    priority=2,
    block=True
)

@disable_bn.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    if not args:
        await disable_bn.finish("需要参数.")
    msg = handle_enabled(event.self_id, f'{event.group_id}', False, args)
    await disable_bn.finish(msg, reply_message=True)


get_b = on_regex(
    r"^[A-z]{2,}/[A-z]{2,}$",
    flags=re.I,
    priority=5,
    block=False
)

@get_b.handle()
async def _(event: MessageEvent):
    args = event.get_plaintext().upper()
    a, b = args.split("/")
    if a == b:
        return
    symbol = a + b
    try:
        res: str = client.ticker_price(symbol)["price"]
        await get_b.finish(res, reply_message=True)
    except ClientError as e:
        logger.debug(e.error_message)
    except ActionFailed as e:
        logger.error(err_info(e))


class _cron:
    second, minute, hour, day, month = account.binance_cron.split()


_status_lock = asyncio.Lock()


@scheduler.scheduled_job(
    "cron",
    id="BN推送",
    name="BN推送",
    second=_cron.second,
    minute=_cron.minute,
    hour=_cron.hour,
    day=_cron.day,
    month=_cron.month,
    misfire_grace_time=15
)
async def _():
    if _status_lock.locked():
        logger.warning("上一次BN推送尚未结束, 跳过本次推送...")
        return

    async with _status_lock:
        logger.info("正在推送BN币价...")

        now = time.strftime("%Y-%m-%d %H:%M:%S")

        for self_id in enabled:
            try:
                bot = get_bot(self_id)
            except Exception as e:
                logger.exception(e)
                bot = None

            if bot:
                for uid in list(enabled[self_id]):
                    if not enabled[self_id][uid]:
                        continue
                    try:
                        node = list()
                        symbols = [i.replace("/", "") for i in enabled[self_id][uid]]
                        prices = {
                            i["symbol"]: i["price"]
                            for i in client.ticker_price(symbols=symbols)
                        }
                        for symbol in prices:
                            try:
                                node.append(
                                    MessageSegment.node_custom(
                                        2854196310,
                                        "Q群管家",
                                        f"{now}\n{symbol}: {prices[symbol]}"
                                    )
                                )
                            except Exception as e:
                                logger.error(e)
                                continue

                        if not node:
                            continue
                        await bot.send_forward_msg(group_id=uid, messages=node)

                    except ActionFailed as e:
                        logger.error(e)
                        if e.info.get('msg') == "GROUP_NOT_FOUND":
                            enabled[self_id].pop(uid)
                            save_config()
                        continue

                    except Exception as e:
                        logger.error(e)
                        continue

        logger.info("BN币价推送完毕...")
