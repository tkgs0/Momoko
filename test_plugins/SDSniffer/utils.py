
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   free_stable_diffusion.py
@Time    :   2022/10/09 12:41:12
@Author  :   Ayatale 
@Version :   1.3-diy2
@Contact :   ayatale@qq.com
@Github  :   https://github.com/brx86/
@Desc    :   白嫖 Stable Diffusion
"""


import asyncio, httpx, random, time

# 协程池，限制并发数量
async def sem_gather(task_list, sem_num):
    sem = asyncio.Semaphore(sem_num)

    async def _wrapper(task):
        async with sem:
            return await task

    _task_list = map(_wrapper, task_list)
    return await asyncio.gather(*_task_list)


# 检查网页是否有效且为Stable Diffusion Webui
async def check_html(n):
    async with httpx.AsyncClient() as client:
        for _ in range(3):
            try:
                r = await client.get(url := f"https://{n}.gradio.app")
                break
            except Exception:
                pass
        else:
            return
    if "auth_required" in r.text:
        print(f"Locked:  {url}")
    elif "Stable Diffusion" in r.text:
        print(f"\033[1;32mSuccess: \033[4;34m{url}\033[0m")
        return url
    else:
        return


# 创建任务，随机获取网页
async def run():
    start = random.randint(10000, 24800)
    end = start + 300
    print(f"\033[1;35mScan from {start} to {end}\033[0m")
    task_list = [check_html(n) for n in range(start, end)]
    url_list = list(filter(None, await sem_gather(task_list, 50)))
    return '\n' + '\n'.join(url_list)


def sniff():
    start_time = time.time()
    try:
        msg = asyncio.run(run())
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
    except Exception as e:
        msg = "\n"+repr(e)
    msg += f"\nCosts: {time.time()-start_time:.2f}s"
    print("\033[1;35mComplete\033[0m")
    return msg


if __name__ == "__main__":
    sniff()
