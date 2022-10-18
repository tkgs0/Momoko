from nonebot.adapters.onebot.v11 import unescape

class Funny():

    @staticmethod
    def fake_msg(text: str) -> list:
        arg = text.split("\n")
        node = list()
    
        for i in arg:
            args = i.split("-")
            qq = args[0]
            name = unescape(args[1])
            repo = unescape(args[2].replace("\\n","\n"))
            dic = {"type": "node", "data": {"name": name, "uin": qq, "content": repo}}
            node.append(dic)
        return node