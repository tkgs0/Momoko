import json
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Extra
from nonebot import logger, get_driver

from .download import get_model_list_file


class Config(BaseModel, extra=Extra.ignore):
    nickname: List[str] = ["萝卜子"]
    mockingbird_path: str | Path = Path() / "data" / "mockingbird"
    super_only: Optional[bool] = True  # 是否限制仅超级用户使用
    tencent_secret_id: str = ""
    tencent_secret_key: str = ""


_config = Config.parse_obj(get_driver().config.dict())

NICKNAME = _config.nickname

MOCKINGBIRD_PATH = Path(_config.mockingbird_path)
SUPER_ONLY = _config.super_only
TENCENT_SECRET_ID = _config.tencent_secret_id
TENCENT_SECRET_KEY = _config.tencent_secret_key


class MockingBirdManager:
    def __init__(self, path: Optional[Path]):
        self.model_list = {}
        self.config = {}

        if not path:
            model_list_file = MOCKINGBIRD_PATH / "model_list.json"
            config_file = MOCKINGBIRD_PATH / "config.json"
        else:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            model_list_file = path / "model_list.json"
            config_file = path / "config.json"

        self.model_list_file = model_list_file
        self.config_file = config_file

        self.load_config()
        self.load_model_list()
        
    def init_data(self) -> None:
        """
        初始化配置文件
        """
        self.config = {
            "model": "azusa",
            "voice_accuracy": 9,
            "max_steps": 1000,
        }
        self.save_data()
    
    def load_model_list(self) -> None:
        """
        加载模型列表
        """
        if not self.model_list_file.exists():
            logger.info("Downloading MockingBird model data resource...")
            get_model_list_file(self.model_list_file)
            with open(self.model_list_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(dict()))
                f.close()
        if self.model_list_file.exists():
            with open(self.model_list_file, "r", encoding="utf-8") as f:
                self.model_list = json.load(f)
        self._list = self.get_list()

    def load_config(self) -> None:
        """
        加载配置文件
        """
        if not self.config_file.exists():
            self.init_data()
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)


    def set_config(self, config_name: str, value) -> None:
        """
        更新配置文件
        """
        self.config[config_name] = value
        self.save_data()

    def get_config(self, config_name: str):
        return self.config[config_name]

    def get_list(self) -> list:
        """
        获取模型列表
        """
        info: list =[]
        for model_name in self.model_list:
            info.append(model_name)
        return info

    def get_model_info(self, model_name: str):
        return self.model_list[model_name]

    def save_data(self) -> None:
        """
        保存配置文件
        """
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
        self.load_config()
    
    def update_model_list(self) -> str | bool:
        msg = get_model_list_file(self.model_list_file)
        self.load_model_list()
        return msg

Manager = MockingBirdManager(MOCKINGBIRD_PATH)
