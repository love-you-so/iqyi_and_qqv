# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import random
import time
import traceback
import os
import requests
from scrapy import signals
import pymysql
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from qqv.settings import DATABASE


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


class ProxyMiddleware(object):
    '''
    设置Proxy
    '''
    ips = []

    def proxy(self):
        self.p = Proxy()
        ip, id = self.p.get_proxy(1)
        if ip:
            self.ip = ip
            self.ip_id = id
        else:
            self.p.save_proxy(10)
            return self.proxy()

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        return s

    def process_request(self, request, spider):
        self.proxy()
        print('使用代理ip：' + str(self.ip))
        request.meta['proxy'] = self.ip

        pass

    def process_exception(self, request, exception, spider):

        self.p.delete_proxy(self.ip_id)
        return request

    def process_response(self, request, response, spider):

        if response.status in [404, 500, 503]:
            self.p.delete_proxy(self.ip_id)
            return request

        if request.url.endswith('403.htm'):
            self.p.delete_proxy(self.ip_id)

        return response


class Save:

    def __init__(self):
        # self.conn = pymysql.connect(host='192.168.1.216',
        #                             port=3306,
        #                             user='cjzcg',
        #                             password='tceng^7Iu96ytes',
        #                             db='tcengvod', charset='utf8', )
        self.conn = pymysql.connect(
            host=DATABASE.get('host'),
            port=DATABASE.get('port'),
            user=DATABASE.get('user'),
            password=DATABASE.get('password'),
            db=DATABASE.get('db'),
            charset=DATABASE.get('charset'),
        )
        self.curs = self.conn.cursor()

    def log(self, mes):
        file = 'qq_m.log'
        file_dir = os.getcwd() + '/runtime/'
        self.video_mkdir(file_dir)

        file = str(file_dir) + str(file)
        with open(file, 'a') as f:
            f.write(mes)
            f.write('\n')

    def query(self, sql):
        self.curs.execute(sql)
        # self.log(sql)
        return self.curs, self.conn

    # 创建文件夹
    def video_mkdir(self, path):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 判断路径是否存在
        # 存在     True
        # 不存在   False
        isExists = os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            return False

    def insert(self, dic, table):
        k = list(dic.keys())
        v = list(dic.values())
        for i in range(len(v)):
            if v[i] == None:
                v[i] = ' '
            elif isinstance(v[i], int):
                v[i] = str(v[i])
            v[i] = "'" + str(v[i]) + "'"
        ks = ','.join(k)
        vs = ','.join(v)
        ks = '(' + ks + ')'
        vs = '(' + vs + ')'
        n_sql = 'insert into %s %s values %s ' % (table, ks, vs)
        return n_sql

    def insertall(self, lis, table):
        ks = ''
        vvs = ''

        for dic in lis:
            k = list(dic.keys())
            v = list(dic.values())
            for i in range(len(v)):
                if v[i] == None:
                    v[i] = ' '
                elif isinstance(v[i], int):
                    v[i] = str(v[i])

                v[i] = "'" + str(v[i]) + "'"
            ks = ','.join(k)
            vs = ','.join(v)
            ks = '(' + ks + ')'
            vs = '(' + vs + '),'
            vvs += vs
        kks = ks
        n_sql = 'insert into %s %s values %s ' % (table, kks, vvs)
        if n_sql.endswith(', '):
            n_sql = n_sql[:-2]

        return n_sql

    def select(self, table, *select, where):
        sele = ''
        for i in select:
            sele += i + ', '
        if sele.endswith(', '):
            sele = sele[:-2]

        sql = f'select {sele} from {table} where {where}'

        return sql

    def update(self, dic: dict, table, where):
        s = ''
        try:
            dic.pop('collection_time_add')
        except Exception:
            try:
                dic.pop('vod_time_add')
            except Exception:
                pass
        for k, v in dic.items():
            if v == None:
                v = ''
            elif isinstance(v, int):
                v = str(v)
            elif isinstance(v, float):
                v = str(v)
            v = "'" + str(v) + "'"
            ss = k + '=' + v + ', '
            s += ss

        if s.endswith(', '):
            s = s[:-2]

        # n_sql = f'update {table} set {s} where vod_iqiyi_albumId = {albumId} or vod_douban_albumId = ' \
        #           f'{albumId} or vod_yk_albumId={albumId} or vod_tx_albumId={albumId}'

        n_sql = f'update {table} set {s} where {where}'
        return n_sql

    def save(self, dic, table, where=None, *select):
        # 判断是否存在
        if where:
            sql = self.select(table, *select, where=where)
            self.query(sql=sql)
            old = self.curs.fetchone()
        else:
            old = None
        # 存储或者更新
        if old:
            n_sql = self.update(dic, table, where)
        else:
            if isinstance(dic, dict):
                n_sql = self.insert(dic, table)
            elif isinstance(dic, list):
                n_sql = self.insertall(dic, table)
            else:
                return
        print(n_sql)
        self.query(sql=n_sql)
        # 查找本次操作的id
        try:
            sql = self.select(table, *('id', 'vod_name'), where=where)
            self.query(sql=sql)
            id, vod_name = self.curs.fetchall()[0]
            return id, vod_name

        except Exception as e:
            return
        finally:
            self.conn.commit()

    def close(self):
        self.conn.close()


class Proxy:

    def __init__(self):
        self.save = Save()
        self.table = 'port_log'

    def typeof(self, variate):
        type = None
        if isinstance(variate, int):
            type = "int"
        elif isinstance(variate, str):
            type = "str"
        elif isinstance(variate, float):
            type = "float"
        elif isinstance(variate, list):
            type = "list"
        elif isinstance(variate, tuple):
            type = "tuple"
        elif isinstance(variate, dict):
            type = "dict"
        elif isinstance(variate, set):
            type = "set"
        return type

    def str_to_json(self, data):
        return json.loads(data)

    # 获取ip

    def save_proxy(self, num=10):
        time.sleep(2)
        proxies = []  # 存储代理IP
        # 芝麻代理
        # urlPort = random.choice([1, 11])  # 1 http 11 https
        urlPort = 11  # 1 http 11 https
        url = 'http://webapi.http.zhimacangku.com/getip?num={}&type=2&pro=0&city=0&yys=0&port={}&time=1&ts=1&ys=1&cs=1' \
              '&lb=1&sb=0&pb=45&mr=2&regions=110000,130000,140000,210000,230000,310000,320000,330000,340000,350000,' \
              '360000,370000,410000,420000,430000,440000,500000,510000,530000,610000 '.format(num, urlPort)
        res = requests.get(url=url, timeout=(2, 30), verify=False)
        # 成功
        if res.status_code == 200:
            proxyData = res.text
            if proxyData and self.typeof(proxyData) == 'str':
                proxyData = self.str_to_json(proxyData)
                if proxyData['code'] == 0:  # 成功获取数据
                    for pIndex in range(len(proxyData['data'])):
                        pInstall = {}  # 插入数据
                        pStr = proxyData['data'][pIndex]
                        pInstall['ip'] = str(pStr['ip']).strip()
                        pInstall['port'] = str(pStr['port']).strip()
                        # pInstall['city'] = str(pStr['city']).strip()
                        # pInstall['isp'] = str(pStr['isp']).strip()
                        pInstall['expire_time'] = str(pStr['expire_time']).strip()
                        pInstall['type'] = 1  # 芝麻
                        pInstall['state'] = 1  # ok
                        proxies.append(pInstall)
        # # 拼接
        # for proxiesIndex in range(len(proxies)):
        #     proxiesStr = proxies[proxiesIndex]
        # proxies[proxiesIndex]['proxy_https'] = 'https://' + str(proxiesStr['ip']) + ':' + str(proxiesStr['port'])
        # proxies[proxiesIndex]['proxy_http'] = 'http://' + str(proxiesStr['ip']) + ':' + str(proxiesStr['port'])
        print(proxies)
        s = self.save.save(proxies, self.table)
        return proxies

    def get_proxy(self, num=1):

        # sql = self.save.select('port_log', 'ip', 'port', 'id', where='state=1')
        sql = f'select ip, port, id from {self.table}'
        curs, conn = self.save.query(sql)
        try:
            ip, port, id = curs.fetchone()
            return 'https://' + ip + ':' + port, id
        except TypeError:
            return None, None

    def delete_proxy(self, id):
        sql = f'delete from {self.table} where id={id}'
        cursql, conn = self.save.query(sql)
        conn.commit()
