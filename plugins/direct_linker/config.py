from pydantic import BaseModel, Extra
from typing import List
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    linker_group: List[int] = []
    linker_command: str = 'link'


config = Config.parse_obj(get_driver().config.dict())


linker_group = config.linker_group
linker_command = config.linker_command

