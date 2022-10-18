from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11.helpers import Cooldown
from nonebot.plugin import on_regex
import time
import random



setu = on_regex(r'^[色涩瑟][图圖]$|^[来來发發给給]((?P<num>\d+)|(?:.*))[张張个個幅点點份丶](?P<keyword>.*?)[色涩瑟][图圖]$', rule=to_me(), priority=5, block=True)

@setu.handle([Cooldown(120, prompt="慢...慢一..点❤")])
async def _(event: MessageEvent):
    await setu.send("正在拉取涩图, 请稍后...", at_sender=True)
    time.sleep(random.randint(5,15))
    await setu.finish("Error: 涩图太涩, 发不出去力...")