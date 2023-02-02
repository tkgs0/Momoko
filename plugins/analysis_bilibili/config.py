from typing import List
from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.allow):
    analysis_blacklist: List[int] = []
    analysis_group_blacklist: List[int] = []
    analysis_display_image: bool = False
    analysis_display_image_list: List[str] = []


config = Config.parse_obj(get_driver().config.dict())
