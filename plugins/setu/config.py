from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    setu_cooldown: int = 60
    setu_withdraw: int = 60
    lolicon_r18: int = 2
    pixproxy: str = ''
    acggov_token: str = 'apikey'
