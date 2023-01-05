from typing import List

from nonebot import get_driver
from nonebot.config import BaseConfig


class Config(BaseConfig):

    analysis_blacklist: List[int] = []
    analysis_group_blacklist: List[int] = []
    analysis_display_image: bool = False
    analysis_display_image_list: List[str] = []

    class Config:
        extra = "allow"


config = Config(**get_driver().config.dict())
