from pathlib import Path
import os
import random
try:
    import ujson as json
except ModuleNotFoundError:
    import json

resource = os.path.join(os.path.dirname(__file__), "resource")

Major_Arcana = json.load(open(Path(resource) / "Major_Arcana.json", "r", encoding="utf8"))
Unusual = json.load(open(Path(resource) / "Unusual.json", "r", encoding="utf8"))
Major_list = ["愚人", "魔术师", "女祭司", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界", "草莓", "礼物", "启明", "飞猪", "白日梦", "迷你象"]

Wands = json.load(open(Path(resource) / "Minor_Arcana" / "Wands.json", "r", encoding="utf8"))
Pentacles = json.load(open(Path(resource) / "Minor_Arcana" / "Pentacles.json", "r", encoding="utf8"))
Cups = json.load(open(Path(resource) / "Minor_Arcana" / "Cups.json", "r", encoding="utf8"))
Swords = json.load(open(Path(resource) / "Minor_Arcana" / "Swords.json", "r", encoding="utf8"))


Minor_list = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]

class Tarot():
    @staticmethod
    def get_tarot():
        mj = random.randint(0,len(Major_list)-1)
        major = None
        img = None
        if mj < 22: 
            major = Major_Arcana[Major_list[mj]]
            img = Path(resource) / "image" / f"{mj}.png"
        else:
            major = Unusual[Major_list[mj]]
            img = Path(resource) / "image" / "22.png"
        wand = Wands[random.choice(Minor_list)]
        pentacle = Pentacles[random.choice(Minor_list)]
        cup = Cups[random.choice(Minor_list)]
        sword = Swords[random.choice(Minor_list)]
        content = [
            "锵锵锵，塔罗牌的预言是~",
            f"{major['title']}\n[CQ:image,file=file:///{img}]\n{wand['title']}\n{pentacle['title']}\n{cup['title']}\n{sword['title']}",
            "以下为牌面解析~",
            f"{major['title']}\n{major['analysis']}",
            f"{wand['title']}\n{wand['analysis']}",
            f"{pentacle['title']}\n{pentacle['analysis']}",
            f"{cup['title']}\n{cup['analysis']}",
            f"{sword['title']}\n{sword['analysis']}"
        ]
        node = list()
        for i in content:
            dic = {
                "type": "node",
                "data": {
                    "user_id": "2854200812",
                    "nickname": "灯塔",
                    "content": i
                }
            }
            node.append(dic)
        return node
        
