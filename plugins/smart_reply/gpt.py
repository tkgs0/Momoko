from pathlib import Path
import ujson as json
from revChatGPT import V1
from nonebot import get_driver

from .config import Config

V1.log.info = V1.log.debug

config = Config.parse_obj(get_driver().config.dict())

usr = config.chatgpt_usr
pwd = config.chatgpt_pwd

filepath = Path() / "data" / "smart_reply" / "chatlist.json"
filepath.parent.mkdir(parents=True, exist_ok=True)

'''
{
    chatlist: {
        user: [conversation_id, parent_id]
    }
}
'''
default_chatlist: dict = {"chatlist": {}}
chatlist = (
    json.loads(filepath.read_text("utf-8"))
    if filepath.is_file()
    else default_chatlist
)
chatlist = (
    chatlist 
    if chatlist.keys() == default_chatlist.keys() 
    else default_chatlist
)

keyword = (Path(__file__).parent / "resource" / "keyword.txt").read_text("utf-8").split("\n")

chatbot = (
    V1.Chatbot(config={"email": usr, "password": pwd})
    if usr and pwd
    else None
)

    
def save_chat():
    filepath.write_text(json.dumps(chatlist), "utf-8")


def get_chat(msg: str, uid: str) -> str:
    if not chatbot:
        return "未配置openai帐号, 请联系Bot管理员."

    user = chatlist["chatlist"].get(uid)
    cid = user[0] if user else None
    pid = user[1] if user else None
    
    try:
        chatbot.reset_chat()
        text = ""
        for data in chatbot.ask(msg, cid, pid):
            text = data["message"]
        chatlist["chatlist"].update({uid: [chatbot.conversation_id, chatbot.parent_id]})
    except Exception as e:
        return repr(e)

    save_chat()

    for i in keyword:
        text = text.replace(i, "░"*len(i))
    return text


def clear_chat(uid: str) -> str | None:
    if not chatbot:
        return "未配置openai帐号, 请联系Bot管理员."

    if not (user := chatlist["chatlist"].get(uid)):
        return
    try:
        chatbot.delete_conversation(user[0])
    except Exception as e:
        return repr(e)
    chatlist["chatlist"].pop(uid)
    save_chat()


def clear_all_chat() -> str | None:
    if not chatbot:
        return "未配置openai帐号."

    try:
        chatbot.clear_conversations()
    except Exception as e:
        return repr(e)
    chatlist["chatlist"].clear()
    save_chat()
