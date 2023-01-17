from nonebot.adapters.onebot.v11 import unescape

class Funny():

    @staticmethod
    def fake_msg(text: str) -> list:
        arg = text.strip().split("\n")
        node = list()
    
        for i in arg:
            args = i.split("-")
            if is_number(args[0]):
                qq = args[0]
            else:
                raise TypeError('qq号须为数字!')
            name = unescape(args[1])
            repo = unescape(args[2].replace("\\n","\n"))
            dic = {"type": "node", "data": {"name": name, "uin": qq, "content": repo}}
            node.append(dic)
        return node


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
