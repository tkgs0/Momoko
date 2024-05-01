from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_alconna")

from .__main__ import HELP_TEXT  # noqa: E402
from .config import ConfigModel  # noqa: E402

__version__ = "0.2.0.post1"
__plugin_meta__ = PluginMetadata(
    name="CallAPI",
    description="使用指令来调用 Bot 的 API",
    usage=HELP_TEXT,
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-callapi",
    type="application",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"License": "MIT", "Author": "student_2333"},
)
