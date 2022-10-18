
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   naifu_free.py
@Time    :   2022/10/11 16:13:34
@Author  :   Ayatale 
@Version :   1.5
@Contact :   ayatale@qq.com
@Github  :   https://github.com/brx86/
@Desc    :   白嫖 Naifu（也有概率是Stable Diffusion）
'''

# 设置并发数，建议不要超过50
POOL = 20


import asyncio, httpx, random, time

# 协程池，限制并发数量
async def sem_gather(task_list, sem_num):
    sem = asyncio.Semaphore(sem_num)

    async def _wrapper(task):
        async with sem:
            # 等待随机时间，避免同时大量请求
            await asyncio.sleep(random.random())
            return await task

    _task_list = map(_wrapper, task_list)
    return await asyncio.gather(*_task_list)


# 检查网页是否有效且为Stable Diffusion WebUI或Naifu
async def check_html(n):
    for _ in range(3):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url := f'http://bore.pub:{n}')
                if 'auth_required' in r.text:
                    print(f'Lock:  {url}')
                    return
                elif 'NAIFU' in r.text and 'novelai' in r.text:
                    print(f'\033[1;32mNaifu: \033[4;34m{url}\033[0m')
                    return f'Naifu: {url}'
                elif 'Stable Diffusion' in r.text:
                    print(f'\033[1;32mSD:    \033[4;34m{url}\033[0m')
                    return f'SD: {url}'
                else:
                    print(f'\033[1;33m{n}:\033[0m unknown', end='\r', flush=True)
                    return
        except (httpx.RemoteProtocolError, httpx.ConnectError):
            print(f'\033[1;33m{n}:\033[0m empty  ', end='\r', flush=True)
            return
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            print(f'\033[1;33m{n}:\033[0m timeout', end='\r', flush=True)
            pass
        except Exception as e:
            print(f'\033[1;33m{n}:\033[1;31m {e.__class__.__name__}\033[0m')


# 创建任务，随机获取网页
async def run():
    start = random.randint(33000, 42000)
    end = start + 1000
    print(f'\033[1;35mScan from {start} to {end}\033[0m')
    task_list = [check_html(n) for n in range(start, end)]
    url_list = list(filter(None, await sem_gather(task_list, POOL)))
    return '\n' + '\n'.join(url_list)


if __name__ == "__main__":
    start_time = time.time()
    try:
        asyncio.run(run())
        print(f"Costs: {time.time()-start_time:.2f}s")
    except KeyboardInterrupt:
        print("Exiting...")
        print(f"Costs: {time.time()-start_time:.2f}s")
        exit(0)
    except Exception as e:
        print(repr(e))