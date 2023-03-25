from httpx import AsyncClient


Headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 YaBrowser/23.0.0.00.00 SA/3 Safari/537.36"
}


async def get_github_reposity_information(url: str) -> str:
    try:
        UserName, RepoName = url.replace("github.com/", "").split("/")
        async with AsyncClient() as client:
            res = await client.get(f"https://api.github.com/users/{UserName}", headers=Headers, timeout=5)
            RawData = res.json()
            AvatarUrl = RawData["avatar_url"]
            ImageUrl = f"https://image.thum.io/get/width/1280/crop/640/viewportWidth/1280/png/noanimate/https://socialify.git.ci/{UserName}/{RepoName}/image?description=1&font=Rokkitt&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&pulls=1&stargazers=1&theme=Dark&logo={AvatarUrl}"
            await res.aclose()
            return ImageUrl
    except Exception:
        return "获取信息失败"


async def get_url(url: str) -> str | bytes:
    async with AsyncClient() as client:
        res = await client.get(url, headers=Headers, timeout=30)
        img = res.content
        await res.aclose()
        return img
