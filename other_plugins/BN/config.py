from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    binance_key: str = ""
    binance_secret_key: str = ""
    binance_cron: str ="0 0 20 * *"


"""
cron 格式

* * * * *
秒 分 时 日 月

month (1-12)

day of month (1-31)

hour (0-23)

minute (0-59)

second (0-59)

"""
