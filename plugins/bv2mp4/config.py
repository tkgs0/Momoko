from pydantic import BaseModel, ConfigDict
from pathlib import Path


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")
    bv_dir: Path | str = Path() / "bv_downloads"
    ffmpeg_path: Path | str = ""
