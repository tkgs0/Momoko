from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.v11.helpers import Cooldown
from nonebot.params import CommandArg
from nonebot.plugin import on_command

from random import choice
import requests



url = 'http://tc.tfkapi.top/API/qqqz.php?type=json&qq='

_flmt_notice = choice(['慢...慢一..点❤', '冷静1下', '歇会歇会~~'])



qqqz = on_command('查权重', priority=5, block=True)

@qqqz.handle([Cooldown(10, prompt=_flmt_notice)])
async def _(event: MessageEvent, arg: Message = CommandArg()):
    msg = _check(event, arg)
    await qqqz.finish(msg)



def _check(event, arg):
    msg = event.get_message()
    msg1 = arg.extract_plain_text()

    if msg1 == '自己':
        try:
            res = int(requests.post(url=f'{url}{event.user_id}').json()['qz'])
            return f'查询结果: {res}'
        except:
            return '查询失败'

    uids = [at.data['qq'] for at in msg['at']]

    if not uids:
        uids = msg1.strip().split()
        if not uids:
            return '用法:\n查权重 qq qq1 qq2 ...'

    uids = list(set(uids))
    for uid in uids:
        if not is_number(uid):
            return '格式错误, id必须为纯数字'

    result = list()
    for uid in uids:
        
        try:
            res = int(requests.post(url=url+uid).json()['qz'])
            result.append(f'{uid} 查询结果: {res}')
        except:
            result.append(f'{uid} 查询失败')
    return '\n'.join(result)



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
