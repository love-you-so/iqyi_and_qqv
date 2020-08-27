运行方式 在qqv文件夹下运行命令 scrapy crawl qqv

在pipelines.py 中配置数据库
```python
import pymysql
class Save:
    def __init__(self):
        self.conn = pymysql.connect(host='#',
                                    port='#',
                                    user='#',
                                    password='#',
                                    db='#', charset='utf8', )
        self.curs = self.conn.cursor()

```


