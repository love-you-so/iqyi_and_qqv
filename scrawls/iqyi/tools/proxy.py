import base64
import json
import time

import requests

# 判断类型
from tools.mian_db import Save
def getTime(seconds):
    timeArray = time.localtime(seconds)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

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
        # urlPort = 11  # 1 http 11 https
        # url = 'http://webapi.http.zhimacangku.com/getip?num={}&type=2&pro=0&city=0&yys=0&port={}&time=1&ts=1&ys=1&cs=1' \
        #       '&lb=1&sb=0&pb=45&mr=2&regions=110000,130000,140000,210000,230000,310000,320000,330000,340000,350000,' \
        #       '360000,370000,410000,420000,430000,440000,500000,510000,530000,610000 '.format(num, urlPort)
        # res = requests.get(url=url, timeout=(2, 30), verify=False)
        # # 成功
        # if res.status_code == 200:
        #     proxyData = res.text
        #     if proxyData and self.typeof(proxyData) == 'str':
        #         proxyData = self.str_to_json(proxyData)
        #         print(proxyData)
        #         if proxyData['code'] == 0:        # 成功获取数据
        #             for pIndex in range(len(proxyData['data'])):
        #                 pInstall = {}             # 插入数据
        #                 pStr = proxyData['data'][pIndex]
        #                 pInstall['ip'] = str(pStr['ip']).strip()
        #                 pInstall['port'] = str(pStr['port']).strip()
        #                 # pInstall['city'] = str(pStr['city']).strip()
        #                 # pInstall['isp'] = str(pStr['isp']).strip()
        #                 pInstall['expire_time'] = str(pStr['expire_time']).strip()
        #                 pInstall['type'] = 1      # 芝麻
        #                 pInstall['state'] = 1     # ok
        #                 proxies.append(pInstall)
        # # 拼接
        # for proxiesIndex in range(len(proxies)):
        #     proxiesStr = proxies[proxiesIndex]
            # proxies[proxiesIndex]['proxy_https'] = 'https://' + str(proxiesStr['ip']) + ':' + str(proxiesStr['port'])
            # proxies[proxiesIndex]['proxy_http'] = 'http://' + str(proxiesStr['ip']) + ':' + str(proxiesStr['port'])
        code = base64.b64encode(bytes('17072799087:0cc0648cb52f7334f5ad009148678266', 'utf-8'))
        urls = 'http://api2.uuhttp.com:39002/index/api/return_data?mode=http&count=10&b_time=120&return_type=2&line_break=6&ttl=1&secert={}'.format(
            code.decode())
        ru = requests.get(urls, timeout=(6, 60))
        if ru.status_code == 200:
            ru_data = json.loads(str(ru.text).replace("(s\/秒)", ''))
            for pIndex in range(len(ru_data)):
                pStr = ru_data[pIndex]
                pInstall = {'ip': pStr['ip'], 'port': pStr['port']}  # 插入数据
                t = getTime(int(time.time()) + int(pStr['timeout']))
                pInstall['expire_time'] = t
                pInstall['type'] = 3  # uu
                pInstall['state'] = 1  # ok
                print(pInstall)
                proxies.append(pInstall)

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


if __name__ == '__main__':
    p = Proxy()
    # p.save_proxy(2)
    ip, id = p.get_proxy(1)
    p.delete_proxy(id)




