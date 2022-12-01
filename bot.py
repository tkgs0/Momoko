#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter


nonebot.init()
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
nonebot.load_plugins("basic_plugins")
nonebot.load_plugins("plugins")
nonebot.load_plugin("haruka_bot")
nonebot.load_plugins("other_plugins")


if __name__ == "__main__":
    nonebot.run(app="__mp_main__:app")
