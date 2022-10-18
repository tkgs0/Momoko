import re



class MessageChecker:
    """
    检查所传回的信息是否存在被注入可能
    """
    tenc_gchat_url: str = "gchat.qpic.cn"
    may_inject_keys: list = ["record", "video", "music", "xml", "json"]
    def __init__(self, text: str):
        self.text = text

    @property
    def check_cq_code(self) -> bool:
        _type = re.findall(r"CQ:(.*?),", self.text)
        for i in _type:
            if i == "image":
                result = re.findall(r"url=(.*?)]", self.text)
                url = "" if not result else result[0]
                if self.tenc_gchat_url not in url:
                    return False
                else:
                    return True
            if i in self.may_inject_keys:
                return False
            else:
                return True
        else:
            return True

    @property
    def check_image_url(self) -> bool:
        if self.tenc_gchat_url not in self.text:
            return False
        else:
            return True
