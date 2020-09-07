import asyncio


class Command:

    def run(self):
        loop = asyncio.get_event_loop()
        asyncio.run(loop)


def xxx():
    return 12




if __name__ == '__main__':
    # cmd = Command()
    # cmd.run()
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, xxx)
    print(future)
    print(future.done())
    def ll(n):
        print(n)
        print('xxx')
        return 13

    async def xxxxx(future):
        future.add_done_callback(ll)
        await future
    loop.run_until_complete(xxxxx(future))
    print(future.done())
