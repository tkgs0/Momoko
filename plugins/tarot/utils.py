from nonebot.adapters.onebot.v11 import MessageSegment
from pathlib import Path
from random import randint, choice
try:
    import ujson as json
except ModuleNotFoundError:
    import json


resource = Path(__file__).parent /  "resource"


Major_Arcana = json.loads((resource / "Major_Arcana.json").read_text("utf-8"))
Unusual = json.loads((resource / "Unusual.json").read_text("utf-8"))

Major_list = ["愚人", "魔术师", "女祭司", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界", "草莓", "礼物", "启明", "飞猪", "白日梦", "迷你象"]


Minor_Arcana = resource / "Minor_Arcana"

Wands = json.loads((Minor_Arcana / "Wands.json").read_text("utf-8"))
Pentacles = json.loads((Minor_Arcana / "Pentacles.json").read_text("utf-8"))
Cups = json.loads((Minor_Arcana / "Cups.json").read_text("utf-8"))
Swords = json.loads((Minor_Arcana / "Swords.json").read_text("utf-8"))

Minor_list = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]



class Tarot():
    @staticmethod
    def get_tarot(uid: int, name: str):
        mj = randint(0,len(Major_list)-1)
        major = None
        img = None
        if mj < 22: 
            major = Major_Arcana[Major_list[mj]]
            img = Path(resource) / "image" / f"{mj}.png"
        else:
            major = Unusual[Major_list[mj]]
            img = Path(resource) / "image" / "22.png"
        wand = Wands[choice(Minor_list)]
        pentacle = Pentacles[choice(Minor_list)]
        cup = Cups[choice(Minor_list)]
        sword = Swords[choice(Minor_list)]
        content = [
            "锵锵锵，塔罗牌的预言是~",
            f"{major['title']}\n{MessageSegment.image(img)}\n{wand['title']}\n{pentacle['title']}\n{cup['title']}\n{sword['title']}",
            "以下为牌面解析~",
            f"{major['title']}\n{major['analysis']}",
            f"{wand['title']}\n{wand['analysis']}",
            f"{pentacle['title']}\n{pentacle['analysis']}",
            f"{cup['title']}\n{cup['analysis']}",
            f"{sword['title']}\n{sword['analysis']}"
        ]
        node = [
            {
                "type": "node",
                "data": {
                    "name": name,
                    "uin": str(uid),
                    "content": msg
                }
            }
            for msg in content
        ]
        return node
        
