# import asyncio
#
# def yyy(n):
#     for i in range(n):
#         yield i
#
# async def zzz(n):
#     print('zzz: ', n)
#     await asyncio.sleep(0.1)
#
# async def xxx(n):
#     print(n)
#     await asyncio.sleep(n)
#     loop = asyncio.get_event_loop()
#     for i in yyy(int(n * 10)):
#         task = loop.create_task(zzz(i))
#         await task
#         asyncio.run_coroutine_threadsafe(task, loop)
#
#
# async def main():
#     task1 = asyncio.create_task(xxx(0.8))
#     task2 = asyncio.create_task(xxx(0.7))
#     task3 = asyncio.create_task(xxx(0.6))
#     task4 = asyncio.create_task(xxx(0.5))
#     task5 = asyncio.create_task(xxx(0.4))
#
#     await task1
#     await task2
#     await task3
#     await task4
#     await task5
#
# if __name__ == '__main__':
#     asyncio.run(main())
#
# import re
#
# s = 'https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=doco&offset=0&pagesize=30&sort=18&itrailer=-1'
#
# itrailer = re.findall('itrailer=-\d+', s)
# print(itrailer)


# s = '''https://list.mgtv.com/3/a1----1----a1-c2-2--a1-.html?channelId=3'''
# d = '''https://list.mgtv.com/3/a1----1----a1-c2-3--a1-.html?channelId=3'''
#
# l = s.split('-')
# print(l)
# l[10] = str(int(l[10])+1)
# ss = '-'.join(l)
# print(ss)
# print(ss==d)
#
# 'https://pcweb.api.mgtv.com/episode/list?_support=10000000&version=5.5.35&video_id=1777090&page=0&size=30&&callback=jsonp_1599099322116_32948'

import requests
res = requests.get(url='https://www.mgtv.com/b/335242/9524028.html')
print(res.text)


