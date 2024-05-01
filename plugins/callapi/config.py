from nonebot import get_plugin_config
from pydantic import BaseModel


class ConfigModel(BaseModel):
    callapi_pic: bool = True


config = get_plugin_config(ConfigModel)
