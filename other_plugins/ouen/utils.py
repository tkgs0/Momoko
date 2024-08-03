from io import BytesIO
from pathlib import Path
from pil_utils import BuildImage


dirname = Path(__file__).parent
png = dirname / 'ouen.jpg'


def edit_img(text: str) -> BytesIO:

    img = BuildImage.open(png)
    img.draw_text(xy=(216, 64, 458, 230), text=text, fontsize=30, max_fontsize=60, min_fontsize=1, allow_wrap=True, lines_align="center", fontname=f"{dirname / 'SourceHanMono-Regular.otf'}")
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
