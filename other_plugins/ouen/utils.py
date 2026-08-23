from io import BytesIO
from pathlib import Path
from pil_utils import BuildImage
from nonebot import get_plugin_config

from .config import Config



fonts = list(get_plugin_config(Config).font_families)
dirname = Path(__file__).parent
png = dirname / 'ouen.jpg'


def edit_img(text: str) -> BytesIO:

    img = BuildImage.open(png)
    img.draw_text(xy=(216, 64, 458, 230), text=text, font_size=30, max_fontsize=60, min_fontsize=1, allow_wrap=True, lines_align="center", font_families=fonts)
    return img.save_png()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        exit(-1)

    img = edit_img(arg)
    img.seek(0)
    (Path() / "output.png").write_bytes(img.read())
