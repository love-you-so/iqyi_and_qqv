# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class QqvSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class QqvDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):

        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):

        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# class ProxyMiddleware(object):
#     '''
#     设置Proxy
#     '''
#     ips = []
#
#     @classmethod
#     def from_crawler(cls, crawler):
#
#         return cls(ip=crawler.settings.get('MY_PROXIES'))
#
#     def process_request(self, request, spider):
#
#         request.meta['proxy'] = self.ip
#
#         pass
#
#     def process_exception(self, request, exception, spider):
#         # print('process_exception',request.url, exception,type(exception), spider)
#         # print('ResponseNeverReceived:::',isinstance(exception,ResponseNeverReceived))
#         # print('ConnectionLost:::',isinstance(exception,ConnectionLost))
#         # print('ConnectionDone:::',isinstance(exception,ConnectionDone))
#         # print('TCPTimedOutError:::',isinstance(exception,TCPTimedOutError))
#         # print('ConnectError:::',isinstance(exception,ConnectError))
#         # print('ConnectionRefusedError:::',isinstance(exception,ConnectionRefusedError))
#         # print('TCPTimedOutError:::',isinstance(exception,TCPTimedOutError))
#         # print('TimeoutError:::',isinstance(exception,TimeoutError))
#
#         if isinstance(exception,ResponseNeverReceived) or isinstance(exception,TypeError) \
#                 or isinstance(exception,ALL_EXCEPTIONS):
#
#             try:
#
#                 proxying = request.meta['proxy']
#                 ProxyMiddleware.ips.remove(proxying)
#                 print(ProxyMiddleware.ips)
#                 self.ip = random.choice(ProxyMiddleware.ips)
#             except IndexError as e:
#                 print(e)
#                 d = ProxyMiddleware.make_ip()
#                 self.ip = random.choice(ProxyMiddleware.ips)
#                 print(self.ip,d)
#             request.meta['proxy'] = self.ip
#
#             return request
#
#         with open('error.txt','a+') as f:
#             f.write(request.url+'\n')
#         pass
#
#     def process_response(self, request, response, spider):
#
#         if response.status in [404,500,503] :
#
#             try:
#                 ProxyMiddleware.ips.remove(self.ip)
#             except ValueError as e:
#                 print(e)
#                 pass
#             return request
#
#         if request.url.endswith('403.htm'):
#
#             try:
#                 ProxyMiddleware.ips.remove(self.ip)
#             except ValueError as e:
#                 print(e)
#                 pass
#             return request
#
#         return response
