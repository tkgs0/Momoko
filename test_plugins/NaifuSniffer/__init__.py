from pathlib import Path
from random import choice
from subprocess import Popen, PIPE, STDOUT

from nonebot import on_command
from nonebot.adapters.onebot.v11.helpers import (
    Cooldown,
    CooldownIsolateLevel
)


_flmt_notice = choice(["慢...慢一..点❤", "冷静1下", "歇会歇会~~"])
file_path = Path(__file__).parent / "fnfs.py"

_fnfs = on_command('>fnfs', priority=5, block=True)

@_fnfs.handle([Cooldown(
    1800,
    prompt=_flmt_notice,
    isolate_level=CooldownIsolateLevel.GLOBAL
)])
async def _():
    opt = "python " + str(file_path)

    content = Popen(
        opt,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        universal_newlines=True
    ).communicate()

    msg = f"\nstdout:\n{content[0]}"
    await _fnfs.finish(msg, at_sender=True)
