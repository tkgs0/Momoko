from pydantic import BaseModel, Extra
from typing import List


class Config(BaseModel, extra=Extra.ignore):
    nickname: List[str] = ['小思']
    superusers: List[str] = []
    xiaoai_voice: bool = False
