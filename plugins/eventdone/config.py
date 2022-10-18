from pathlib import Path
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    conf_path: str = str(Path(__file__).parent / "set.json")