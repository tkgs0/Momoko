from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    binance_key: str = ""
    binance_secret_key: str = ""
