import pymysql
import os


class Save:
    def __init__(self):
        # 测试库
        self.conn = pymysql.connect(host='192.168.1.216',
                                    port=3306,
                                    user='cjzcg',
                                    password='tceng^7Iu96ytes',
                                    db='tcengvod', charset='utf8', )
        # 正式
        # self.conn = pymysql.connect(host='rm-j6co0332808hbxpcwpo.mysql.rds.aliyuncs.com',
        #                             port=3306,
        #                             user='uservide',
        #                             password='CHjduTY793CKLp',
        #                             db='video', charset='utf8mb4', )

        self.curs = self.conn.cursor()

    # def log(self, mes):
    #     file = "aqyi.log"
    #     file_dir = os.getcwd() + '/runtime/'
    #     self.video_mkdir(file_dir)
    #     file = str(file_dir) + str(file)
    #     with open(file, 'a') as f:
    #         f.write(mes)
    #         f.write('\n')
    def log(self, mes, file='aqyi.log', error=''):
        file_dir = os.getcwd() + '/runtime/'
        self.video_mkdir(file_dir)
        file = str(file_dir) + str(file)
        with open(file, 'a', encoding='utf8') as f:
            if mes == None:
                mes = ''
            f.write(mes)
            f.write('\n')
            f.write(error)
            f.write('\n')

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

    # def query(self, sql):
    #     self.log(sql)
    #     self.curs.execute(sql)
    #     return self.curs, self.conn
    def query(self, sql):
        try:
            self.curs.execute(sql)
            self.log(sql)
            return self.curs, self.conn
        except Exception as e:
            mes = 'error>>>>>>>' + sql
            self.log(mes, 'error.sql', str(e))
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
