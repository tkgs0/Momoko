from pydantic import BaseModel, ConfigDict
from typing import List


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nickname: List[str] = ['小思']
    superusers: List[str] = []
    sizhi_appid: str = ""
    sizhi_timeout: int = 60
    xiaoai_voice: bool = False
