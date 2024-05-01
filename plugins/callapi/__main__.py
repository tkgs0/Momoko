import json
import traceback
from contextlib import suppress
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

from bbcode import Parser as BBCodeParser
from nonebot import on_command
from nonebot.adapters import Bot, Message, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher, current_bot, current_event
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna.uniseg import UniMessage
from PIL import Image
from pil_utils import BuildImage, Text2Image
from pil_utils.fonts import DEFAULT_FALLBACK_FONTS
from pydantic import BaseModel
from pygments import highlight
from pygments.formatters.bbcode import BBCodeFormatter
from pygments.lexers import get_lexer_by_name

if TYPE_CHECKING:
    from pygments.style import Style

from .config import config

CODE_FONTS = [
    "JetBrains Mono",
    "Cascadia Mono",
    "Segoe UI Mono",
    "Liberation Mono",
    "Menlo",
    "Monaco",
    "Consolas",
    "Roboto Mono",
    "Courier New",
    "Courier",
    "Microsoft YaHei UI",
    *DEFAULT_FALLBACK_FONTS,
]
PADDING = 25

bbcode_parser = BBCodeParser()


@dataclass()
class Codeblock:
    lang: Optional[str]
    content: str


def item_to_plain_text(item: Union[str, Codeblock]) -> str:
    parsed: List[
        Tuple[int, Optional[str], Optional[dict], str]
    ] = bbcode_parser.tokenize(
        f"```{item.lang or ''}\n{item.content}\n```"
        if isinstance(item, Codeblock)
        else item,
    )
    return "".join(
        [
            data
            for b_type, _, _, data in parsed
            if b_type == BBCodeParser.TOKEN_DATA or b_type == BBCodeParser.TOKEN_NEWLINE
        ],
    )


def format_plain_text(items: List[Union[str, Codeblock]]) -> str:
    return "\n".join(item_to_plain_text(it) for it in items)


def item_to_image(item: Union[str, Codeblock]) -> Image.Image:
    item = item or "\n"

    is_codeblock = isinstance(item, Codeblock)
    background_color: Optional[str] = None

    if not is_codeblock:
        formatted = item

    else:
        formatter = BBCodeFormatter()
        style: "Style" = formatter.style
        background_color = getattr(style, "background_color", None)

        formatted: Optional[str] = None
        if item.lang:
            with suppress(Exception):
                lexer = get_lexer_by_name(item.lang)
                formatted = cast(str, highlight(item.content, lexer, formatter))

        if not formatted:
            formatted = item.content

    text_img = Text2Image.from_bbcode_text(
        formatted,
        fallback_fonts=CODE_FONTS,
    )

    if not is_codeblock:
        return text_img.to_image()

    block_size = (text_img.width + PADDING * 2, text_img.height + PADDING * 2)
    block_width, block_height = block_size

    build_img = BuildImage.new("RGBA", block_size, (255, 255, 255, 0))

    if background_color:
        build_img.draw_rounded_rectangle(
            (0, 0, block_width, block_height),
            radius=10,
            fill=background_color,
        )

    text_img.draw_on_image(build_img.image, (PADDING, PADDING))
    return build_img.image


def draw_image(items: List[Union[str, Codeblock]]) -> bytes:
    images = [item_to_image(it) for it in items]

    width = max(img.width for img in images)
    height = sum(img.height for img in images)
    bg = BuildImage.new(
        "RGBA",
        (width + PADDING * 2, height + PADDING * 2),
        (255, 255, 255),
    )

    y = PADDING
    for img in images:
        bg.paste(img, (PADDING, y), alpha=True)
        y += img.height

    return bg.convert("RGB").save("png").getvalue()


async def send_return(items: List[Union[str, Codeblock]]):
    event = current_event.get()
    bot = current_bot.get()

    if config.callapi_pic:
        try:
            # via saa
            image = draw_image(items)
            await UniMessage.image(raw=image).send(reply_to=True, fallback=False)
        except Exception:
            logger.exception(
                "Error when sending image via uniseg, fallback to plain text",
            )
        return

    await bot.send(event, format_plain_text(items))


def cast_param_type(param: str) -> Any:
    if param.isdigit():
        return int(param)

    if param.replace(".", "", 1).isdigit():
        return float(param)

    if param.lower() in ("true", "false"):
        return param.lower() == "true"

    return param


def parse_args(params: str) -> Tuple[str, Dict[str, Any]]:
    lines = params.splitlines(keepends=False)
    api_name = lines[0].strip()
    param_lines = lines[1:]

    try:
        param_dict = json.loads("\n".join(param_lines))
    except Exception:
        param_dict = {}
        for line in param_lines:
            if "=" not in line:
                raise ValueError(  # noqa: B904, TRY200
                    f"参数 `{line}` 格式错误，应为 name=param",
                )

            key, value = line.split("=", 1)
            param_dict[key.strip()] = cast_param_type(value.strip())

    return api_name, param_dict


HELP_ITEMS = [
    "[b]指令格式：[/b]",
    Codeblock(lang=None, content="callapi <API 名称>\n[传入参数]"),
    "关于传入参数的格式，请看下面的调用示例",
    "",
    "[b]调用示例：[/b]",
    "使用 name=value 格式（会自动推断类型）：",
    Codeblock(
        lang=None,
        content=(
            "callapi get_stranger_info\n"
            "[color=#008000][b]user_id[/b][/color]=[color=#666666]3076823485[/color]"
        ),
    ),
    "使用 JSON（可以多行）：",
    Codeblock(
        lang=None,
        content=(
            "callapi get_stranger_info\n"
            '{ [color=#008000][b]"user_id"[/b][/color]: [color=#666666]3076823485[/color] }'
        ),
    ),
]
HELP_TEXT = format_plain_text(HELP_ITEMS)


call_api_matcher = on_command("callapi", permission=SUPERUSER)


@call_api_matcher.handle()
async def _(matcher: Matcher, bot: Bot, args: Message = CommandArg()):
    arg_txt = "".join(
        [
            txt if x.is_text() and (txt := x.data.get("text")) else str(x)
            for x in cast(Iterable[MessageSegment], args)
        ],
    ).strip()

    if not arg_txt:
        await send_return(HELP_ITEMS)
        return

    try:
        api, params_dict = parse_args(arg_txt)
    except ValueError as e:
        await matcher.finish(e.args[0])
    except Exception:
        logger.exception("参数解析错误")
        await matcher.finish("参数解析错误，请检查后台输出")

    ret_items = [
        f"[b]Bot:[/b] {bot.adapter.get_name()} {bot.self_id}",
        "",
        f"[b]API:[/b] {api}",
        "",
        "[b]Params:[/b]",
        Codeblock(
            lang="json",
            content=json.dumps(params_dict, ensure_ascii=False, indent=2),
        ),
        "",
        "[b]Result:[/b]",
    ]

    try:
        result = await bot.call_api(api, **params_dict)
    except Exception:
        formatted = traceback.format_exc().strip()
        ret_items.extend(
            (
                "Call API Failed!",
                Codeblock(lang="pytb", content=formatted),
            ),
        )

    else:
        if isinstance(result, BaseModel):
            result = result.dict()

        content = None
        with suppress(Exception):
            content = json.dumps(result, ensure_ascii=False, indent=2)

        ret_items.append(
            Codeblock(
                lang="json" if content else None,
                content=content or str(result),
            ),
        )

    await send_return(ret_items)
