import scrapy


class QqvItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Tx_vod(scrapy.Item):

     type_pid = scrapy.Field()  # 视频分类 一级 1:电影 2:连续剧 3:综艺 4:动漫 ,
     type_id = scrapy.Field()  # 视频分类 ,
     vod_name = scrapy.Field()    # 视频标题 ,
     vod_sub = scrapy.Field()    # 视频副标题 ,
     vod_en = scrapy.Field()    # 视频别名 如：拼音、英文名 ,
     vod_tag = scrapy.Field()    # 视频标签 ,
     vod_pic = scrapy.Field()    # 视频图片 ,
     vod_pic_thumb = scrapy.Field()   # 视频缩略图 ,
     vod_pic_slide = scrapy.Field()   # 视频海报图 ,
     vod_actor = scrapy.Field()       # 主演列表 ,
     vod_director = scrapy.Field()    # 导演 ,
     vod_writer = scrapy.Field()    # 编剧 ,
     vod_behind = scrapy.Field()    # 幕后 ,
     vod_blurb = scrapy.Field()     # 简介 ,
     vod_remarks = scrapy.Field()    # 备注 ,
     vod_pubdate = scrapy.Field()    # 上映日期 ,
     vod_total = scrapy.Field()  # 总集数 ,
     vod_serial = scrapy.Field()  # 连载数 ,
     vod_tv = scrapy.Field()    # 电视频道 ,
     vod_weekday  = scrapy.Field()    # 节目周期 ,
     vod_area  = scrapy.Field()    # 发行地区 如：大陆,香港 ,
     vod_year = scrapy.Field()    # 上映年代 如：2019 ,
     vod_version = scrapy.Field()    # 影片版本 如：高清版,TV ,
     vod_state = scrapy.Field()    # 资源类别 如：正片,预告片 ,
     vod_duration = scrapy.Field()    # 时长 ,
     vod_isend = scrapy.Field()  # 是否完结 0 未完结 1 完结 ,
     vod_time_add = scrapy.Field()  # 添加时间 ,
     vod_time_up = scrapy.Field()  # 更新时间 ,
     vod_is_from = scrapy.Field()  # 来源 0:默认未标识来源  1:腾讯视频 2 爱奇艺 3 优酷 4 豆瓣 5bibi 6 芒果tv ,
     vod_is_advance = scrapy.Field()  # 是否 超前点播 0 否 1 确定 ,
     vod_is_pay_mark = scrapy.Field()  # 是否 vip 0 否 1是 ,
     vod_douban_albumId = scrapy.Field()    # 目标站视频关键ID 类似豆瓣ID ,
     vod_tx_albumId = scrapy.Field()    # 目标站视频关键ID 类似豆瓣ID ,
     vod_mango_albumId = scrapy.Field()    # 目标站视频关键ID 类似豆瓣ID ,
     vod_iqiyi_albumId = scrapy.Field()    # 目标站视频关键ID 类似豆瓣ID ,
     vod_yk_albumId = scrapy.Field()    # 目标站视频关键ID 类似豆瓣ID ,
     vod_status = scrapy.Field()  # 视频状态 0等待自动检测 1 正常 2 下线 ,
     vod_details = scrapy.Field()  # 爬取数据 详情  json格式 ,
     # vod_time_auto_up = scrapy.Field()  # 自动更新使用


class Tx_vod_collection(scrapy.Item):
     vod_id = scrapy.Field()
     vod_name = scrapy.Field()
     vod_is_from = scrapy.Field()
     albumId = scrapy.Field()
     collection = scrapy.Field()
     collection_title = scrapy.Field()
     collection_url = scrapy.Field()
     collection_type = scrapy.Field()
     collection_is_advance = scrapy.Field()
     collection_is_pay_mark = scrapy.Field()
     collection_is_state = scrapy.Field()
     collection_weight = scrapy.Field()
     collection_last_time = scrapy.Field()
     collection_details = scrapy.Field()
     collection_time_add = scrapy.Field()
     collection_time_up = scrapy.Field()
     collection_status = scrapy.Field()
     vod_tx_albumId = scrapy.Field()

