# coding: utf8
import pymysql
import os

from qqv.items import Tx_vod, Tx_vod_collection

from qqv.settings import DATABASE


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

    def log(self, mes, file='qq.log', dic='{}'):
        file_dir = os.getcwd() + '/runtime/'
        self.video_mkdir(file_dir)

        file = str(file_dir) + str(file)
        with open(file, 'a', encoding='utf8') as f:
            if mes == None:
                mes = ''
            f.write(mes)
            f.write('\n')
            f.write(dic)
            f.write('\n')

    def query(self, sql, dic='{}'):
        try:
            self.curs.execute(sql)
            self.log(sql)
            return self.curs, self.conn
        except Exception:
            mes = 'error>>>>>>>' + sql
            self.log(mes, 'error.sql', dic)
        return None, None

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
        dicc = dic.get('vod_blurb')
        print('save %s' % dic.get('vod_name'))
        self.query(sql=n_sql, dic=dicc)
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


class QqvPipeline:
    def process_item(self, item, spider):

        if isinstance(item, Tx_vod):
            sav = item.__dict__.get('_values')
            albumId = sav.get('vod_tx_albumId')
            save = Save()
            where = f'vod_iqiyi_albumId="{albumId}" or vod_douban_albumId="{albumId}" or vod_yk_albumId="{albumId}" or vod_tx_albumId="{albumId}"'
            id, vod_name = save.save(sav, 'tx_vod', where, 'vod_tx_albumId')
            save.close()
            return item

        elif isinstance(item, Tx_vod_collection):
            sav = item.__dict__.get('_values')
            collection = sav.get('collection')
            try:
                if int(collection) == 31:
                    print(sav.get('vod_name') + '>>>' + collection + '>>>' + sav.get('collection_url'))
            except Exception:
                pass
            vod_tx_albumId = sav.pop('vod_tx_albumId')
            save = Save()
            sql = f'select id from tx_vod where vod_tx_albumId="{vod_tx_albumId}"'
            curs, conn = save.query(sql=sql)
            if curs:
                ids = curs.fetchone()
                if ids:
                    id = ids[0]
                    sav['vod_id'] = id
                    where = f'albumId="{sav.get("albumId")}"'
                    id, vod_name = save.save(sav, 'tx_vod_collection', where, 'albumId', )
                    conn.close()
                    return item
