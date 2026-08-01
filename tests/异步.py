import asyncio
from asyncio import sleep, wait_for, create_task, all_tasks


async def get(timeout):
    await sleep(timeout)
    return 1


async def main1():
    # task1 = asyncio.create_task(get(1))
    # task2 = asyncio.create_task(get(10))
    # task3 = asyncio.create_task(get(20))
    # task4 = asyncio.create_task(get(30))
    task5 = asyncio.create_task(get(40))

    print("开始")
    # print(await task1)
    # print(await task2)
    # print(await task3)
    # print(await task4)
    print(await task5)
    print("Look Me")
    task5.cancel() #取消事件循环任务
    result = await wait_for(task5, timeout=3) #执行超过三秒就报错
    print(result)
    print("结束")

async def color(message):
    print(message)
    await asyncio.sleep(1)
    print(message)


async def nothing():
    await asyncio.sleep(0)
    print('Busy')

async def busy_loop():
    for i in range(10):
        await nothing()

async def normal():
    for i in range(10):
        await asyncio.sleep(0)
        print('normal')


async def main():
    # print(all_tasks())
    print("--- 主函数开始执行   ---")
    await asyncio.gather(
        busy_loop(),
        normal()
    )
    # create_task(color("开始执行"))
    # await sleep(0.5)
    print("----- OVER-----")
   # try:
    #     raise IOError()
    # except*  TypeError as e:
    #     print(e)


if __name__ == '__main__':
    # asyncio.run(main())
    l = [1,2,3]
    i = iter(l)
    print(i)
    print(next(i))
    print(next(i))
    print(next(i))
    print(next(i))