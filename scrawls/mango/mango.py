import asyncio
from asyncio import Queue
from collections import deque

import aiohttp
from settings import urls

from httprequest import HttpResponse, HttpRequest

print(urls)


class Spider:
    start_urls = [
        'http://www.baidu.com'
    ]

    def __init__(self, start_urls):
        self.start_urls = start_urls

    @classmethod
    def format_crawl(cls):
        self = cls(cls.start_urls)
        for url in self.start_urls:
            yield HttpRequest(url=url, callback=self.crawl)

    def crawl(self, response):
        print(response)
        urls = ['https://list.mgtv.com/3/176--------a1-c2-1--a1-.html?channelId=3', 'https://list.mgtv.com/3/175--------a1-c2-1--a1-.html?channelId=3', 'https://list.mgtv.com/3/177--------a1-c2-1--a1-.html?channelId=3', 'https://list.mgtv.com/3/178--------a1-c2-1--a1-.html?channelId=3', 'https://list.mgtv.com/3/43--------a1-c2-1--a1-.html?channelId=3', 'https://list.mgtv.com/3/44--------a1-c2-1--a1-.html?channelId=3', 'https://list.mgtv.com/2/a1-10--------c2-1---.html?channelId=2', 'https://list.mgtv.com/2/a1-12--------c2-1---.html?channelId=2', 'https://list.mgtv.com/2/a1-11--------c2-1---.html?channelId=2', 'https://list.mgtv.com/2/a1-193--------c2-1---.html?channelId=2', 'https://list.mgtv.com/50/a1-52--------c2-1---.html?channelId=50', 'https://list.mgtv.com/50/a1-53--------c2-1---.html?channelId=50', 'https://list.mgtv.com/1/a1-1--------c2-1---.html?channelId=1', 'https://list.mgtv.com/1/a1-2--------c2-1---.html?channelId=1']
        for url in urls:
            yield HttpRequest(url=url, callback=self.crawl1)

    def crawl1(self, response):
        print(response.url)


class Downloader:

    async def download(self, request):
        url = request.url
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, timeout=60) as resp:
                url = str(resp.url)
                response = HttpResponse(request, response=resp)
                return response


class Scheduler:

    def __init__(self, maxsize=10):
        self.maxsize = maxsize

    def open(self):
        self.queue = Queue(maxsize=self.maxsize)

    async def insert(self, request):
        await self.queue.put(request)

    async def pop(self):
        request = await self.queue.get()
        return request

    @property
    def size(self):
        return self.queue.qsize()


class Engine:

    def __init__(self):
        self._close = None
        self.scheduler = None
        self.download = Downloader()
        self.max = 5
        self.crawlling = []

    async def get_response_callback(self,content, request):

        response = HttpResponse(content, request)
        new_requests = request.callback(response)
        for new_request in new_requests:
            if isinstance(new_request, HttpRequest):
                await self.scheduler.insert(new_request)

        self.crawlling.remove(request)

    async def _next_request(self):
        """
        类似递归方法，不断的从调度器中拿请求，然后再回调自己
        """
        if self.scheduler.size == 0 and len(self.crawlling) == 0:
            self._close.callback(None)
            return

        while len(self.crawlling) < self.max:
            request = await self.scheduler.pop()
            if not request:
                return
            self.crawlling.append(request)
            response = await self.download.download(request)
            await self.get_response_callback(response, request)

    async def open_spider(self,spider):
        # 实例化调度器
        self.scheduler = Scheduler()
        # 激活调度器
        self.scheduler.open()
        # 迭代种子列表生成器，将每个请求放入调度器中。
        start_requests = spider.format_crawl()
        for request in start_requests:
            await self.scheduler.insert(request)
            await self._next_request()


if __name__ == '__main__':

    async def main(spider):
        e = Engine()
        task = asyncio.create_task(e.open_spider(spider))
        await task

    asyncio.run(main(Spider))
