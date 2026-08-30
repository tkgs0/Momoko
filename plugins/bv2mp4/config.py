from pydantic import BaseModel, ConfigDict
from pathlib import Path


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")

    bv_cache: Path | str = Path() / "data" / "bv_cache"
    bv_max_workers: str | int = 6
