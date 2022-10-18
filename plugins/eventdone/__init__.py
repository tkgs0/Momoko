import time
import json
import aiofiles
from nonebot import get_driver, get_bot
from nonebot.adapters.onebot.v11 import Bot, FriendRequestEvent, PrivateMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, on_request
from .config import Config

# 配置项
config = Config.parse_obj(get_driver().config.dict())
conf_path = config.conf_path

# 获取超级用户的id
super_id = get_driver().config.superusers

# 获取bot的id
bot_id: str = list(get_driver().config.nickname)[0]


async def friend_request_rule(event: FriendRequestEvent):
    async with aiofiles.open(conf_path, "r", encoding="utf-8") as f:
        obj = json.loads(await f.read())
    add_qq = int(json.loads(event.json())["user_id"])
    qq_set = set(obj["add_qq_req_list"]["qq"])
    return add_qq not in qq_set



# 超级用户推送添加机器人好友请求事件
add_friend = on_request(friend_request_rule, priority=1, block=True)


@add_friend.handle()
async def _(bot: Bot, event: FriendRequestEvent):
    try:
        async with aiofiles.open(conf_path, "r", encoding="utf-8") as f:
            obj = json.loads(await f.read())
        qq_list = list(obj["add_qq_req_list"]["qq"])
        add_req = json.loads(event.json())
        add_qq = add_req["user_id"]
        qq_list.append(add_qq)
        comment = add_req["comment"]
        flag = add_req["flag"]
        realtime = time.strftime("%Y年%m月%d日 %H:%M:%S", time.localtime(add_req["time"]))
        obj["add_qq_req_list"]["qq"] = qq_list
        obj["add_qq_req_list"]["flag"] = flag
        async with aiofiles.open(conf_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(obj, indent=4))
        for su_qq in super_id:
            await bot.send_private_msg(user_id=int(su_qq),
                                        message=f"QQ：{add_qq} 请求添加{bot_id}为好友!\n请求添加时间：{realtime}\n验证信息为：{comment}")
    except Exception as e:
        for su_qq in super_id:
            await bot.send_private_msg(user_id=int(su_qq), message=f"{bot_id}坏掉了\n错误信息：{e}")


# 超级用户使用，同意好友添加机器人请求
agree_qq_add = on_command("同意", permission=SUPERUSER)


@agree_qq_add.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    try:
        async with aiofiles.open(conf_path, "r", encoding="utf-8") as f:
            obj = json.loads(await f.read())
        qq_set = set(obj["add_qq_req_list"]["qq"])
        flag = obj["add_qq_req_list"]["flag"]
        user_id = int(event.get_user_id())
        agree_id = int(str(event.get_message()).split("同意")[-1])          #在QQ上同意时请加上申请人QQ号
        if agree_id in qq_set:
            await bot.send_private_msg(user_id=user_id, message=f"机器人成功添加QQ:{agree_id}为好友！")
            await bot.set_friend_add_request(flag=flag, approve=True, remark="")
            obj["add_qq_req_list"]["qq"] = list(qq_set)
            obj["add_qq_req_list"]["flag"] = ""
            async with aiofiles.open(conf_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(obj, indent=4))
        else:
            await bot.send_private_msg(user_id=user_id, message=f"QQ:{agree_id}不在好友申请列表！")
    except Exception as e:
        for su_qq in super_id:
            await bot.send_private_msg(user_id=int(su_qq), message=f"{bot_id}出错了\n错误信息：{e}")
