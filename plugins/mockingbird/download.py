import json
import httpx
from pathlib import Path

from nonebot.log import logger

headers: dict = {
    "User-Agent": "Mozilla/5.0 (Linux; arm64; Android 12; SM-S9080) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 YaBrowser/23.0.0.00.00 SA/3 Mobile Safari/537.36",
}

base_url: str = "https://pan.yropo.top/source/mockingbird/"

class DownloadError(Exception):
    pass

async def download_url(url: str, path: Path) -> bool:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                url = (await client.post(url, headers=headers)).url  # type: ignore
                path.parent.mkdir(parents=True, exist_ok=True)
                async with client.stream(
                    'GET', url=url, headers=headers, timeout=30
                ) as resp:
                    if not resp.content:
                        await resp.aclose()
                        continue
                    with open(path, 'wb') as fd:  # 写入文件
                        async for chunk in resp.aiter_bytes(1024):
                            fd.write(chunk)
                    logger.info(f"Success downloading {url} .. Path：{path.absolute()}")
                    await resp.aclose()
                    return True
            except Exception as e:
                logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
    return False

# 下载资源
async def download_resource(root: Path, model_name: str, model_info: dict):
    for file_name in ["g_hifigan.pt", "encoder.pt"]:
        if not (root / file_name).exists():
            logger.info(f"{file_name}不存在，开始下载{file_name}...请不要退出...")
            res = await download_url(url=base_url + file_name, path=root / file_name)
            if not res:
                return False
    for file_name in ["record.wav", f"{model_name}.pt"]:
        if not (root / model_name / file_name).exists():
            logger.info(f"{file_name}不存在，开始下载{file_name}...请不要退出...")
            if file_name == "record.wav":
                url = model_info["url"]["record_url"]
            else:
                url = model_info["url"]["model_url"]
            res = await download_url(url, root / model_name / file_name)
            if not res:
                return False
    return True
    
# 检查资源是否存在
async def check_resource(root: Path, model_name: str):
    for file_name in ["g_hifigan.pt", "encoder.pt"]:
        if not (root / file_name).exists():
            return False
    for file_name in ["record.wav", f"{model_name}.pt"]:
        if not (root / model_name / file_name).exists():
            return False
    return True

# 更新模型列表文件
def get_model_list_file(file_path: Path) -> str | bool:
    url: str = "https://github.com/AkashiCoin/nonebot_plugin_mockingbird/raw/master/nonebot_plugin_mockingbird/resource/model_list.json"

    url1: str = "https://raw.fastgit.org/AkashiCoin/nonebot_plugin_mockingbird/master/nonebot_plugin_mockingbird/resource/model_list.json"

    with httpx.Client() as client:
        try:
            try:
                data = client.get(
                    url, headers=headers, follow_redirects=True
                ).json()
            except:
                data = client.get(url1, headers=headers).json()
            if data:
                file_path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    "utf-8"
                )
                return True
            else:
                return "更新模型列表失败..."
        except Exception as e:
            logger.error(f"Error downloading {url} .. Error: {e}")
            return "更新模型列表失败..."
