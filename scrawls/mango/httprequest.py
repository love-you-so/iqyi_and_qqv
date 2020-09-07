import aiohttp
import asyncio


def obsolete_setter(setter, attrname):
    '''
    这个函数就是为了在给url赋值的时候能够提示不可以赋值， url只是其中之一body之类的也可以用，算是一个封装
    '''
    def newsetter(self, value):
        c = self.__class__.__name__
        msg = "%s.%s is not modifiable, use %s.replace() instead" % (c, attrname, c)
        raise AttributeError(msg)
    return newsetter


class HttpRequest:

    def __init__(self, url, callback=None, headers=None, meta=None):
        self._set_url(url)
        self._callback = callback
        self._meta = dict(meta) if meta else None
        self._headers = headers

    @property
    def callback(self):
        return self._callback

    @property
    def meta(self):
        '''
        为了在访问mata的时候进入这个函数
        所以赋值时是在init中赋的值，如果不是字典在dict处就会抛出异常，这个方法实现了在为None时可以返回空字典
        '''
        if self._meta is None:
            self._meta = {}

        return self._meta

    def _get_url(self):
        '''
        获得url
        '''
        return self._url

    def _set_url(self, url):

        if not isinstance(url, str):
            raise TypeError('Request url must be str or unicode, got %s:' % type(url).__name__)

        self._url = url

    url = property(_get_url, obsolete_setter(_set_url, 'url'))


class HttpResponse:

    def __init__(self, request, response=None, headers=None, meta=None):
        self._set_url(request.url)
        self._response = response
        self._headers = headers

    @property
    async def text(self):
        return await self._response.text

    @property
    def content(self):
        return self._response.content

    @property
    def read(self):
        return self._response.read

    @property
    async def json(self):
        return await self._response.json

    def _get_url(self):
        '''
        获得url
        '''
        return self._url

    def _set_url(self, url):
        if not isinstance(url, str):
            raise TypeError('Response url must be str or unicode, got %s:' % type(url).__name__)

        self._url = url

    url = property(_get_url, obsolete_setter(_set_url, 'url'))










