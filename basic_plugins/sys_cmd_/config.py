from pydantic import BaseModel

class Config(BaseModel):
    sys_cmd_sh: str = "/sh"
    sys_cmd_cmd: str = "/cmd"
