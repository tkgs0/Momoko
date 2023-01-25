from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    lolicon_r18: int = 2
    pixproxy: str = ''
    acggov_token: str = 'apikey'
