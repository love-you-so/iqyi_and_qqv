启动方式在iqyi下python new_aqyi.py
tools.main_db,py配置数据库
```python
import pymysql
class Save:
    def __init__(self):
        self.conn = pymysql.connect(host='192.168.1.216',
                                    port=3306,
                                    user='cjzcg',
                                    password='tceng^7Iu96ytes',
                                    db='tcengvod', charset='utf8', )
        self.curs = self.conn.cursor()

```