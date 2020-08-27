import pymysql


class Save:
    def __init__(self):
        self.conn = pymysql.connect(host='192.168.1.216',
                                    port=3306,
                                    user='cjzcg',
                                    password='tceng^7Iu96ytes',
                                    db='tcengvod', charset='utf8', )
        self.curs = self.conn.cursor()

    def log(self, mes):
        with open('../../aqyi.log', 'a') as f:
            f.write(mes)
            f.write('\n')

    def query(self, sql):
        self.curs.execute(sql)
        self.log(sql)
        return self.curs, self.conn

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