from pydantic import BaseModel, ConfigDict
from typing import List


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    font_families: List[str] = ['LXGW WenKai Mono GB Screen']
