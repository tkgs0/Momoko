from pydantic import BaseModel

class Config(BaseModel):
    call_http_call: str = "/call"
