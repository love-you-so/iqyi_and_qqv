import json
import re
import time
import scrapy
from lxml import etree
from scrapy import Request

from qqv.items import Tx_vod, Tx_vod_collection


class DmozSpider(scrapy.spiders.Spider):
    name = "qqv"
    allowed_domains = ["dmoz.org"]

    start_urls = [
        'https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=tv&iarea=814&listpage=2&offset=0&pagesize=30&sort=18'
    ]
    channel_ids = {
        '1': {'channel': 'movie',
              'itype': {'7': 100004, '8': 100005, '6': 100061, '9': 100012, '10': 100007, '12': 100006, '11': 100018},
              'iarea': {'内地': 100004, '中国香港': 100025, '美国': 100029, '欧洲': 100032, '中国台湾': 100026, '日本': 100027,
                        '韩国': 100028, '印度': 100030, '泰国':100031, '法国':16, '英国': 15, '德国':17,'意大利':20,
                        '澳大利亚':21,'北欧':22, '拉丁美洲':23,'其他':100033}
              },
        '2': {'channel': 'tv', 'iarea': {'13': 814, '14': [14, 817], '15': [10, 818], '16': [815, 816], '24': 9}},
        '23': {'channel': 'doco', 'itrailer': {'0': -1}},
        '4': {'channel': 'cartoon', 'iarea': {'19': 1, '20': 2, '22': 3}},
        '3': {'channel': 'variety', 'iarea': {'25': 1, '28': 2}},  # 国内和海外
        '5': {'channel': 25},
    }

    def parse(self, response):

        for type_pid, v in self.channel_ids.items():
            urls = []
            # if type_pid in ['1', '2', '23', '4', '']:
            if type_pid in ['1']:
                continue
            channel = v.get('channel')
            iarea = v.get('iarea')
            itrailer = v.get('itrailer',)
            itype = v.get('itype', )

            url = f'https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel={channel}&offset=0&pagesize=30&sort=18'

            if iarea:
                for k, v in iarea.items():
                    if channel in ['tv', 'cartoon', 'variety']:
                        type_id = k
                        url1 = url + '&rarea=' + str(v)
                        urls.append({'url': url1, 'type_id': type_id})

                    elif channel == 'movie':
                        url1 = url + '&rarea=' + str(v)
                        if itype:
                            for k, v in itype.items():
                                type_id = k
                                url2 = url1 + '&itype=' + str(v)
                                urls.append({'url': url2, 'type_id': type_id})
                    else:
                        return

            elif itrailer:
                for k, v in itrailer.items():
                    type_id = k
                    url1 = url + '&itrailer=' + str(v)
                    urls.append({'url': url1, 'type_id': type_id})
            else:
                return

            for url in urls:
                yield Request(url.get('url'), self.next_pages, dont_filter=True, meta={'type_id':url.get('type_id'), 'type_pid':type_pid})
                return

    def next_pages(self, response):
        type_pid = response.meta.get('type_pid')
        type_id = response.meta.get('type_id')
        html = etree.HTML(response.text)
        pages = html.xpath('//div[@class="mod_pages"]/button/@data-offset')
        url = response.url
        for page in pages[1: -1]:
            next_url = url.split('offset=')[0] + f'offset={str(page)}' + url.split('offset=')[1][1:]
            yield Request(next_url, self.parse_page, dont_filter=True,
                    meta={'type_id': type_id, 'type_pid': type_pid})

    def parse_page(self, response):
        type_pid = response.meta.get('type_pid')     # 视频分类 一级 1:电影 2:连续剧 3:综艺 4:动漫
        type_id = response.meta.get('type_id')       # 视频分类
        html = etree.HTML(response.text)
        divs = html.xpath('//div[@class="mod_figure mod_figure_v_default mod_figure_list_box"]/div[@class="list_item"]')
        for div in divs:
            vod_name = div.xpath('a/@title')[0]                # 视频名称
            vod_tx_albumId = div.xpath('a/@data-float')[0]     # 视频唯一id
            url = div.xpath('a/@href')                         # 视频地址
            vod_pic = 'http:' + div.xpath('a/img/@src')[0]   # 视频图片

            mark = div.xpath('a/img')
            if len(mark) <= 1:
                vod_is_pay_mark = 0   # vip
                vod_is_advance = 0    # 超前点播
            else:
                cls = mark[1].xpath('@class')[0]
                if cls.endswith('mark_v_VIP'):
                    vod_is_pay_mark = 1
                    vod_is_advance = 0
                else:
                    vod_is_pay_mark = 1
                    vod_is_advance = 1
            try:
                now_collect = div.xpath('a/div[@class="figure_caption"]/text()')[0]

                if now_collect.startswith('全'):
                    vod_isend = 1
                    vod_serial = ''        # 连载
                else:
                    vod_isend = 0
                    vod_serial = re.findall('\d+', now_collect)[0]
            except IndexError:
                vod_isend = 1
                vod_serial = ''

            meta = {
               'type_pid': type_pid,  'type_id': type_id, 'vod_name': vod_name, 'vod_tx_albumId': vod_tx_albumId,
                'vod_pic': vod_pic, 'vod_is_pay_mark': vod_is_pay_mark, 'vod_is_advance': vod_is_advance,
                'vod_isend': vod_isend, 'vod_serial': vod_serial
            }
            next_url = f'https://node.video.qq.com/x/api/float_vinfo2?cid={vod_tx_albumId}'
            yield Request(url=next_url, callback=self.lists, dont_filter=True, meta=meta)

    def lists(self, response):
        jjson = json.loads(response.text)
        meta = response.meta
        vod_tx_albumId = meta.get('vod_tx_albumId')
        vod_sub = ''        # 视频副标题
        vod_en = ''         # 视频别名
        vod_actors = jjson.get('nam')
        vod_actor = ''        # 主演
        for i in vod_actors:
            if isinstance(i, str):
                vod_actor += i + ','
            elif isinstance(i, list):
                for j in i:
                    vod_actor += j + ','
        vod_actor = vod_actor.replace(r'\n', '').replace(r'\r', '').\
            replace('\\"', '').replace("'", '').replace('\\', '')
        vod_pic_thumb = ''              # 缩略图
        vod_pic_slide = ''              # 海报图
        vod_tv = ''                     # 电视频道
        vod_weekday = ''                # 周期
        vod_area = ''                   # 地区
        vod_version = ''                # 版本， 高清 tv
        vod_director = ''               # 导演
        vod_writer = ''                 # 编剧
        vod_behind = ''                 # 幕后
        typ = jjson.get('typ')

        if typ:
            vod_tag = typ[0]
            try:
                if isinstance(typ[1], str):
                    vod_tag += ',' + typ[1]
                else:
                    for i in typ[1]:
                        vod_tag += ',' + i
            except IndexError:
                pass
        else:
            vod_tag = ''

        try:
            vod_blurb = jjson.get('c', {}).get('description').replace(r'\n', '').replace(r'\r', '').\
                replace('\\"', '').replace("\'", '').replace("’", '').replace(r'\u', '').replace('\\', '')   # 简介
        except AttributeError:
            vod_blurb = ''
        vod_remarks = ''                # 备注
        vod_pubdate = ''                # 上映日期
        video_ids = jjson.get('c', {}).get('video_ids', [])
        vod_total = len(video_ids)    # 总集数
        vod_is_from = 1                 # 视频来源
        vod_time_add = int(time.time())      # 添加时间
        vod_time_up = int(time.time())       # 更新时间
        vod_duration = ''               # 时长
        vod_state = ''                  # 资源类别
        vod_year = jjson.get('c', {}).get('year', '')      # 上映年代
        vod_status = 0                  # 视频状态
        vod_details = json.dumps(jjson, ensure_ascii=False).replace(r'\n', '').replace(r'\r', '').\
            replace('\\"', '').replace("'", '').replace('\\', '')                # 爬取数据
        tx_item = Tx_vod()
        tx_item['type_pid'] = meta.get('type_pid')
        tx_item['type_id'] = meta.get('type_id')
        tx_item['vod_name'] = meta.get('vod_name')
        tx_item['vod_tx_albumId'] = vod_tx_albumId
        tx_item['vod_pic'] = meta.get('vod_pic')
        tx_item['vod_pic_thumb'] = vod_pic_thumb
        tx_item['vod_pic_slide'] = vod_pic_slide
        tx_item['vod_tv'] = vod_tv
        tx_item['vod_weekday'] = vod_weekday
        tx_item['vod_area'] = vod_area
        tx_item['vod_version'] = vod_version
        tx_item['vod_state'] = vod_state
        tx_item['vod_is_pay_mark'] = meta.get('vod_is_pay_mark')
        tx_item['vod_is_advance'] = meta.get('vod_is_advance')
        tx_item['vod_isend'] = meta.get('vod_isend')
        tx_item['vod_serial'] = meta.get('vod_serial')
        tx_item['vod_sub'] = vod_sub
        tx_item['vod_en'] = vod_en
        tx_item['vod_actor'] = vod_actor
        tx_item['vod_director'] = vod_director
        tx_item['vod_writer'] = vod_writer
        tx_item['vod_behind'] = vod_behind
        tx_item['vod_tag'] = vod_tag
        tx_item['vod_blurb'] = vod_blurb
        tx_item['vod_remarks'] = vod_remarks
        tx_item['vod_pubdate'] = vod_pubdate
        tx_item['vod_total'] = vod_total
        tx_item['vod_is_from'] = vod_is_from
        tx_item['vod_time_add'] = vod_time_add
        tx_item['vod_time_up'] = vod_time_up
        tx_item['vod_duration'] = vod_duration
        tx_item['vod_year'] = vod_year
        tx_item['vod_status'] = vod_status
        tx_item['vod_details'] = vod_details
        collect_url = f'https://v.qq.com/x/cover/{vod_tx_albumId}.html'
        collect_page = vod_total//30
        yield Request(url=collect_url, callback=self.collect_list, dont_filter=True,
                      meta={'tx_item': tx_item, 'firstcoolects': 1})
        for i in range(1, collect_page+1):

            if collect_page != vod_total/30:
                collctlast_id = video_ids[30 * i]

                url = f'https://v.qq.com/x/cover/{vod_tx_albumId}/{collctlast_id}.html'
                print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'+url)
                yield Request(url=url, callback=self.collect_list, dont_filter=True,
                              meta={'tx_item': tx_item, 'firstcoolects': 0})

    def collect_list(self, response):
        tx_item = response.meta.get('tx_item')
        htmll = response.text
        html = etree.HTML(response.text)
        try:
            vod_directoree = html.xpath('//li[@class="mod_summary intro_item"]/div[@class="director"]/text()')[0]
            if '导演' in vod_directoree:
                vod_director = html.xpath('//li[@class="mod_summary intro_item"]/div[@class="director"]/a/text()')[0]
            else:
                vod_director = ''
        except IndexError as e:
            vod_director = ''

        tx_item['vod_director'] = vod_director.replace("'", '')
        collects_spans = html.xpath('//div[@class="mod_episode"]/span')

        vod_tx_albumId = tx_item['vod_tx_albumId']


        if not collects_spans:
            collects = html.xpath('//div[@class="mod_figure mod_figure_list mod_figure_list_sm" and @_wind="columnname=选集"]/ul[@class="figure_list"]/li')
            if collects:
                collect = collects[0]
                duration = collect.xpath('a[@class="figure"]/div[@class="figure_count"]/span/text()')
                if duration:
                    duration = duration[0]
                else:
                    duration = ''
                mark_v = collect.xpath('a[@class="figure"]/i[@class="mark_v"]/img/@src')
                if not mark_v:
                    vod_state = 1  # 资源类型， 1正片 2预告片
                    isend = 1
                else:
                    src = mark_v[0]
                    if 'text_yu' in src:
                        vod_state = 2
                        isend = 0

                    else:
                        vod_state = 1
                        isend = 1

            else:
                duration = ''
                vod_state = 1
                isend = 1

            tx_item['vod_state'] = vod_state
            tx_item['vod_isend'] = isend
            tx_item['vod_duration'] = duration

        # if response.meta.get('firstcoolects', 0) == 1:
        #     yield tx_item

        areas = html.xpath('//div[@class="video_tags _video_tags"]')
        print(response.url + str(len(areas)))
        areas = html.xpath('//div[@class="video_tags _video_tags"]/span')
        print(response.url + str(len(areas)))
        areas = html.xpath('//div[@class="video_tags _video_tags"]/span/text()')
        try:
            area = areas[0]
        except IndexError:
            areas = html.xpath('//div[@class="video_tags _video_tags"]/span/text()')
            try:
                area = areas[0]
            except IndexError:
                area = ''
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' + area)


        yield tx_item
        if collects_spans:
            for collects_span in collects_spans:
                vod_id = 0
                vod_name = tx_item['vod_name']                        # 视频名称
                vod_is_from = tx_item['vod_is_from']                  # 来源
                albumId = collects_span.xpath('@id')[0]            # 集id
                collectionss = collects_span.xpath('a/text()')       # 集

                collection_title = ''  # 每集标题
                if collectionss:
                    try:
                        collection = re.findall(r'\d+', collectionss[0])[0]
                    except IndexError:
                        collection = 0
                        collection_title = re.findall(r'\w+', collectionss[0])[0]
                else:
                    collection = 0

                collection_urls = collects_span.xpath('a/@href')    # 每集url
                if collection_urls:
                    collection_url = 'https://v.qq.com' + collection_urls[0]
                else:
                    collection_url = ''

                mark_v = collects_span.xpath('i/img/src')
                if not mark_v:
                    collection_is_pay_mark = 0     # 是否为vip
                    collection_is_state = 1        # 资源类型， 1正片 2预告片
                else:
                    src = mark_v[0]
                    if 'text_yu' in src:
                        collection_is_pay_mark = 0
                        collection_is_state = 2
                    else:
                        collection_is_pay_mark = 1
                        collection_is_state = 1

                collection_weight = 0  # 权重
                collection_type = 0    # 1 标清 2 高清 3超清 4 蓝光 5 4k
                collection_is_advance = 0  # 是否是超前点播
                collection_time_add = time.time()
                collection_time_up = time.time()
                collection_status = 0
                collection_details = json.dumps({'details': {}}).replace(r'\n', '').replace(r'\r', '').\
            replace('\\"', '').replace("'", '').replace('\\', '')                # 爬取数据
                collection_last_time = ''  # 目标资源站最后更新时间

                tx_vod_collection_item = Tx_vod_collection()
                tx_vod_collection_item['vod_id'] = vod_id
                tx_vod_collection_item['vod_name'] = vod_name
                tx_vod_collection_item['vod_is_from'] = vod_is_from
                tx_vod_collection_item['albumId'] = albumId
                tx_vod_collection_item['collection'] = collection
                tx_vod_collection_item['collection_title'] = collection_title.replace(r'\n', '').replace(r'\r', ''). \
                    replace('\\"', '').replace("'", '').replace('\\', '')  # 爬取数据
                tx_vod_collection_item['collection_url'] = collection_url
                tx_vod_collection_item['collection_type'] = collection_type
                tx_vod_collection_item['collection_is_advance'] = collection_is_advance
                tx_vod_collection_item['collection_is_pay_mark'] = collection_is_pay_mark
                tx_vod_collection_item['collection_is_state'] = collection_is_state
                tx_vod_collection_item['collection_weight'] = collection_weight
                tx_vod_collection_item['collection_last_time'] = collection_last_time
                # tx_vod_collection_item['collection_details'] = collection_details
                tx_vod_collection_item['collection_time_add'] = collection_time_add
                tx_vod_collection_item['collection_time_up'] = collection_time_up
                tx_vod_collection_item['collection_status'] = collection_status
                tx_vod_collection_item['vod_tx_albumId'] = vod_tx_albumId

                yield tx_vod_collection_item

        else:
            type_pid = tx_item['type_pid']
            if type_pid == '1':
                collects = html.xpath('//div[@class="mod_figure mod_figure_list mod_figure_list_sm" and @_wind="columnname=选集"]/ul[@class="figure_list"]/li')
            elif type_pid == '3':
                collects = html.xpath(
                    '//div[@class="mod_figure mod_figure_list mod_figure_list_sm"]/ul[@class="figure_list" and @_wind="columnname=往期"]/li')
                print(collects)
            for collect in collects:
                duration = collect.xpath('a[@class="figure"]/div[@class="figure_count"]/span/text()')
                if duration:
                    duration = duration[0]
                else:
                    duration = ''

                vod_id = 0
                vod_name = tx_item['vod_name']  # 视频名称
                vod_is_from = tx_item['vod_is_from']  # 来源
                albumId = collect.xpath('@id')  # 集id
                collection_urls = collect.xpath('a[@class="figure"]/@href')  # 每集url
                if collection_urls:
                    collection_url = 'https://v.qq.com' + collection_urls[0]
                else:
                    collection_url = ''


                if albumId:
                    albumId = albumId[0]
                else:
                    try:
                        path = collection_urls[0]
                        idd = re.findall(r'/\w+.html', path)[0]
                        albumId = idd[1:-5]
                    except Exception:
                        albumId = ''
                collection = 0  # 集
                # collection_title = collect.xpath('a/div[@class="figure_detail_three_row"]/strong/text()')  # 每集标题
                collection_title = collect.xpath('a/img/@alt')  # 每集标题
                if collection_title:
                    collection_title = collection_title[0].replace(r'\n', '').replace(r'\r', ''). \
                    replace('\\"', '').replace("'", '').replace('\\', '')  # 爬取数据
                else:
                    collection_title = ''

                mark_v = collect.xpath('a[@class="figure"]/i[@class="mark_v"]/img/@src')

                if not mark_v:
                    collection_is_pay_mark = 0  # 是否为vip
                    collection_is_state = 1  # 资源类型， 1正片 2预告片
                else:
                    src = mark_v[0]
                    if 'text_yu' in src:
                        collection_is_pay_mark = 0
                        collection_is_state = 2
                    else:
                        collection_is_pay_mark = 1
                        collection_is_state = 1

                collection_weight = 0  # 权重
                collection_type = 0  # 1 标清 2 高清 3超清 4 蓝光 5 4k
                collection_is_advance = 0  # 是否是超前点播
                collection_time_add = time.time()
                collection_time_up = time.time()
                collection_status = 0
                collection_details = json.dumps({'details': {}}).replace(r'\n', '').replace(r'\r', ''). \
                    replace('\\"', '').replace("'", '').replace('\\', '')  # 爬取数据
                collection_last_time = ''  # 目标资源站最后更新时间

                tx_vod_collection_item = Tx_vod_collection()
                tx_vod_collection_item['vod_id'] = vod_id
                tx_vod_collection_item['vod_name'] = vod_name
                tx_vod_collection_item['vod_is_from'] = vod_is_from
                tx_vod_collection_item['albumId'] = albumId
                tx_vod_collection_item['collection'] = collection
                tx_vod_collection_item['collection_title'] = collection_title
                tx_vod_collection_item['collection_url'] = collection_url
                tx_vod_collection_item['collection_type'] = collection_type
                tx_vod_collection_item['collection_is_advance'] = collection_is_advance
                tx_vod_collection_item['collection_is_pay_mark'] = collection_is_pay_mark
                tx_vod_collection_item['collection_is_state'] = collection_is_state
                tx_vod_collection_item['collection_weight'] = collection_weight
                tx_vod_collection_item['collection_last_time'] = collection_last_time
                # tx_vod_collection_item['collection_details'] = collection_details
                tx_vod_collection_item['collection_time_add'] = collection_time_add
                tx_vod_collection_item['collection_time_up'] = collection_time_up
                tx_vod_collection_item['collection_status'] = collection_status
                tx_vod_collection_item['vod_tx_albumId'] = vod_tx_albumId

                yield tx_vod_collection_item

