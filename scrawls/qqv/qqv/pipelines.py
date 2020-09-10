# coding: utf8
import json

import pymysql

from qqv.items import Tx_vod, Tx_vod_collection

from qqv.settings import DATABASE


class Save:
    def __init__(self):
        # self.conn = pymysql.connect(host='192.168.1.216',
        #                             port=3306,
        #                             user='cjzcg',
        #                             password='tceng^7Iu96ytes',
        #                             db='tcengvod', charset='utf8', )
        self.host = DATABASE.get('host')
        self.conn = pymysql.connect(
            host=DATABASE.get('host'),
            port=DATABASE.get('port'),
            user=DATABASE.get('user'),
            password=DATABASE.get('password'),
            db=DATABASE.get('db'),
            charset=DATABASE.get('charset'),
            )
        self.curs = self.conn.cursor()

    def log(self, mes, file='tx.log', error=''):
        with open(file, 'a', encoding='utf8') as f:
            if mes == None:
                mes = ''
            f.write(mes)
            f.write('\n')
            f.write(error)
            f.write('\n')

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
        n_sql = f'update {table} set {s} where {where}'
        return n_sql

    def save(self, dic, table, where=None, *select, returns=('id', 'vod_name')):
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
        print(n_sql[:15])
        print('save %s in %s' % (dic.get('vod_name'), self.host))
        self.query(sql=n_sql)
        # 查找本次操作的id
        try:
            sql = self.select(table, *returns, where=where)
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
            if not albumId:
                albumId = sav.get('vod_mango_albumId')
            print(albumId)
            save = Save()
            vod_details = sav.pop('vod_details', {})  # 取出json
            # where = f'vod_iqiyi_albumId="{albumId}" or vod_douban_albumId="{albumId}" or vod_yk_albumId="{albumId}" or vod_tx_albumId="{albumId}" or vod_mango_albumId = "{albumId}"'
            where = f'vod_iqiyi_albumId="{albumId}" or vod_douban_albumId="{albumId}" or vod_yk_albumId="{albumId}" or vod_tx_albumId="{albumId}" or vod_mango_albumId = "{albumId}"'
            if sav.get('vod_tx_albumId'):
                # vod_id, vod_name = save.save(sav, 'tx_vod', where, 'vod_tx_albumId')
                vod_id, vod_name = save.save(sav, 'iqy_vod', where, 'vod_tx_albumId')
            elif sav.get('vod_mango_albumId'):
                # vod_id, vod_name = save.save(sav, 'tx_vod', where, 'vod_mango_albumId')
                vod_id, vod_name = save.save(sav, 'iqy_vod', where, 'vod_mango_albumId')

            if vod_details:
                where = f'vod_id={vod_id}'
                if isinstance(vod_details, dict):
                    vod_details = json.dumps(vod_details)
                # save.save({'vod_id': vod_id, 'vod_details': vod_details}, 'tx_vod_json', where, 'vod_id', returns=('id', ))  # 存储json
                save.save({'vod_id': vod_id, 'vod_details': vod_details}, 'iqy_vod_json', where, 'vod_id', returns=('id', ))  # 存储json
            save.close()
            return item

        elif isinstance(item, Tx_vod_collection):
            sav = item.__dict__.get('_values')
            print('----------------------------------------')
            collection = sav.get('collection')
            try:
                if int(collection) == 31:
                    print(sav.get('vod_name') + '>>>' + collection + '>>>' + sav.get('collection_url'))
            except Exception:
                pass

            try:
                vod_tx_albumId = sav.pop('vod_tx_albumId')
            except KeyError:
                vod_tx_albumId = None
            try:
                vod_mango_albumId = sav.pop('vod_mango_albumId')
            except KeyError:
                vod_mango_albumId = None

            save = Save()

            if vod_tx_albumId:
                sql = f'select id from iqy_vod where vod_tx_albumId="{vod_tx_albumId}"'
            elif vod_mango_albumId:
                sql = f'select id from iqy_vod where vod_mango_albumId="{vod_mango_albumId}"'

            curs, conn = save.query(sql=sql)
            print('curs', curs)

            if curs:
                ids = curs.fetchone()
                print(ids)
                if ids:
                    id = ids[0]
                    sav['vod_id'] = id
                    where = f'albumId="{sav.get("albumId")}"'
                    try:
                        collection_details = sav.pop('collection_details')
                    except KeyError:
                        collection_details = json.dumps({}, ensure_ascii=False)
                    # collection_id, vod_name = save.save(sav, 'tx_vod_collection', where, 'albumId')

                    collection_id, vod_name = save.save(sav, 'iqy_vod_collection', where, 'albumId')
                    # save.save({'collection_id': collection_id, 'collection_details': collection_details},
                    #             table='tx_vod_collection_json')
                    save.save({'collection_id': collection_id, 'collection_details': collection_details},
                                table='iqy_vod_collection_json')
                    conn.close()
                    return item
