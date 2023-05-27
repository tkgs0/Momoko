from typing import List

from httpx import AsyncClient
from PicImageSearch import Ascii2D
from PicImageSearch.model import Ascii2DResponse

from .config import config
from .utils import async_lock, get_image_bytes_by_url, handle_img, shorten_url


@async_lock()
async def ascii2d_search(url: str, client: AsyncClient) -> List[str]:
    ascii2d_color = Ascii2D(client=client)
    _file = await get_image_bytes_by_url(url)
    color_res = await ascii2d_color.search(file=_file)
    if not color_res.raw:
        return ["Ascii2D 暂时无法使用"]

    resp_text, resp_url, _ = await ascii2d_color.get(
        color_res.url.replace("/color/", "/bovw/")
    )
    bovw_res = Ascii2DResponse(resp_text, resp_url)

    return await get_final_res(color_res) + await get_final_res(bovw_res, True)


async def get_final_res(res: Ascii2DResponse, bovw: bool = False) -> List[str]:
    final_res_list: List[str] = []
    for r in res.raw:
        if not (r.title or r.url_list):
            continue

        thumbnail = await handle_img(r.thumbnail)
        if not config.hide_img and thumbnail.startswith("预览图链接"):
            continue

        title = r.title
        if r.url_list and title == r.url_list[0][1]:
            title = ""

        source = r.url or (r.url_list and r.url_list[0][0])
        source = await shorten_url(source) if source else ""

        author = r.author
        if author and r.author_url:
            author_url = await shorten_url(r.author_url)
            author = f"[{author}]({author_url})"

        res_list = [
            thumbnail,
            r.detail,
            title,
            f"作者：{author}" if author else "",
            f"来源：{source}" if source else "",
        ]
        final_res_list.append("\n".join([i for i in res_list if i]))

        if len(final_res_list) == 3:
            break

    search_type = "特徴" if bovw else "色合"
    result_type = f"Ascii2D {search_type}検索結果"
    result_header = f"{result_type}\n搜索页面：{await shorten_url(res.url)}"
    return [result_header] + final_res_list
