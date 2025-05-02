import asyncio

async def runCoroutine(corountine):
    asyncio.run(corountine)

async def creatTask(coroutine):
    asyncio.create_task(coroutine)

async def blockingTimer(durationSeconds):
    await asyncio.sleep(durationSeconds)

async def readOutputToThread(pipe):
    return (await asyncio.to_thread(pipe.readline)).strip()
