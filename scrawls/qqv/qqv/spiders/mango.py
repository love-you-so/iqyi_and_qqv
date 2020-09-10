import json
import re
import time
from collections import OrderedDict
from pprint import pprint

import scrapy
from lxml import etree
from scrapy import Request

from qqv.items import Tx_vod

from qqv.items import Tx_vod_collection


class MangoSpider(scrapy.spiders.Spider):
    name = "mango"

    start_urls = [
        'https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=tv&iarea=814&listpage=2&offset=0&pagesize=30&sort=18'
    ]
    channel_ids = OrderedDict({
        '1': {'channel_id': 3, 'a1': {'7': 176, '8': 175, '6': 177, '9': 178, '10': 43, '12': 44}},  # 电影在1后边多个b代表资费
        '2': {'channel_id': 2, 'a1': {'13': 10, '14': 12, '15': 11, '24': 193}},
        '23': {'channel_id': 51},  # https://list.mgtv.com/-------------.html?channelId=51
        '4': {'channel_id': 50, 'a1': {'19': 52, '22': 53}},
        '3': {'channel_id': 1, 'a1': {'25': 1, '26': 2}},
        # '5': {'channel_id': 25, 'three_category_id': {'0': ''}},
    })
    starts = {
        '1': {176: 3, 177: 10, 175: 14, 44: 6, 43: 8, 178: 1},
        '23': {0: 11},
        '2': {12: 2, 11: 2, 193: 2, 10: 1, },
        '4': {52: 3, 53: 1 },
        '3': {2: 3, 1: 11, },
    }
    def parse(self, response):

        for type_pid, v in self.channel_ids.items():
            channel_id = v.get('channel_id')
            # if type_pid in ['3', '1', '4', '', '2']:
            if type_pid in ['5']:
                continue
            else:
                if type_pid == '23':
                    url = f'https://list.mgtv.com/51/a1---------c1-1---.html?channelId={channel_id}'
                    yield Request(url=url, callback=self.parse1, meta={'type_pid': type_pid, 'type_id': 0})

                for type_id, vv in v.get('a1', {}).items():
                    if type_pid in [ '1']:
                        url = f'https://list.mgtv.com/{channel_id}/{vv}--------a1-c2-1--a1-.html?channelId={channel_id}'
                    elif type_pid in [ '4']:
                        url = f'https://list.mgtv.com/{channel_id}/a1-{vv}-------a1-c2-1--a1-.html?channelId={channel_id}'
                    else:
                        url = f'https://list.mgtv.com/{channel_id}/a1-{vv}--------c2-1---.html?channelId={channel_id}'  # -的个数不读会影响结果一共13个
                    yield Request(url=url, callback=self.parse1, meta={'type_pid': type_pid, 'type_id': type_id, 'a1': vv})

    def parse1(self, response):

        old_meta = response.meta
        url = response.url
        l = url.split('-')
        type_pid = old_meta.get('type_pid')
        a1 = old_meta.get('a1', 0)
        old_page = l[10]
        x_page = int(self.starts.get(type_pid, {}).get(a1, 0))
        if int(old_page) < x_page:
            page = int(x_page)
            l[10] = str(page)
            next_url = '-'.join(l)
            yield Request(url=next_url, callback=self.parse1, meta=old_meta)
        else:

            page = int(old_page) + 1

            with open('mango_record.log', 'a') as f:
                s = str(type_pid) + '-->' + str(a1) + '-->' + str(page) + '\n'
                f.write(s)

            # if len(lis) < 1:
            #     return

            html = etree.HTML(response.text)
            lis = html.xpath('//div[@class="m-result"]/div[@class="m-result-list"]/ul/li')
            hax_next = 0
            for li in lis:
                hax_next = 1
                vod_name = li.xpath('a[@class="u-title"]/text()')[0]

                if response.meta.get('type_pid') == '3':
                    vod_pic = li.xpath('a[@class="u-video u-video-x"]/img/@src')
                else:
                    vod_pic = li.xpath('a[@class="u-video u-video-y"]/img/@src')
                if vod_pic:
                    vod_pic = 'http:' + vod_pic[0]
                else:
                    vod_pic = ''

                if response.meta.get('type_pid') == '3':
                    mark = li.xpath('a[@class="u-video u-video-x"]/i[@class="mark-v"]')
                else:
                    mark = li.xpath('a[@class="u-video u-video-y"]/i[@class="mark-v"]')
                if mark:
                    pay_mark = mark[0].xpath('text()')[0]
                    if pay_mark == 'VIP':
                        vod_is_pay_mark = 1
                        vod_is_advance = 0
                        vod_state = 1
                    elif pay_mark == '预告':
                        vod_is_pay_mark = 0
                        vod_is_advance = 0
                        vod_state = 0
                    else:
                        vod_is_pay_mark = 0
                        vod_is_advance = 1
                        vod_state = 0
                else:
                    vod_is_pay_mark = 0
                    vod_is_advance = 0
                    vod_state = 0

                vod_actors = li.xpath('span/a')
                vod_actor = ''   # 主演
                for i in vod_actors:
                    try:
                        act = i.xpath('text()')[0]
                    except IndexError:
                        act = ''
                    vod_actor += act + ','
                if vod_actor.endswith(','):
                    vod_actor = vod_actor[:-1]

                if response.meta.get('type_pid') == '3':
                    first_url = li.xpath('a[@class="u-video u-video-x"]/@href')
                else:
                    first_url = li.xpath('a[@class="u-video u-video-y"]/@href')
                if first_url:
                    first_url = 'http:' + first_url[0]
                else:
                    first_url = None

                if first_url:
                    first_video_id = first_url.split('/')[-1].split('.')[0]
                    vod_mango_albumId = first_url.split('/')[-2]

                else:
                    vod_mango_albumId = ''
                    first_video_id = ''

                meta = {
                    'vod_name': vod_name,
                    'vod_pic': vod_pic,
                    'vod_is_pay_mark': vod_is_pay_mark,
                    'vod_is_advance': vod_is_advance,
                    'vod_state': vod_state,
                    'vod_actor': vod_actor,
                    'vod_mango_albumId': vod_mango_albumId,
                    'first_url': first_url,
                    'first_video_id': first_video_id,
                }
                meta.update(old_meta)

                first_url = f'https://pcweb.api.mgtv.com/movie/list?_support=10000000&version=5.5.35&video_id={first_video_id}&page=0&size=30'

                if first_url:

                    yield Request(url=first_url, callback=self.parse2, meta=meta)

                # url = f'https://pcweb.api.mgtv.com/video/info?vid={vid}&cid={vod_mango_albumId}'
                # yield Request(url=url, callback=self.parse4, meta=meta)

            if hax_next == 1:   # 如果又就返回下一页爬取
                l[10] = str(page)
                next_url = '-'.join(l)
                yield Request(url=next_url, callback=self.parse1, meta=old_meta)
            else:
                return

    def parse2(self, response):
        old_meta = response.meta
        jjson = response.json()

        data = jjson.get('data', {})
        lists = data.get('list', [])
        info = data.get('info', {})
        vod_total = data.get('total', 1)
        vod_serial = data.get('count', 1)
        if vod_serial == vod_total:
            vod_isend = 1
        else:
            vod_isend = 0

        vod_is_from = 6
        vod_time_add = int(time.time())      # 添加时间
        vod_time_up = int(time.time())       # 更新时间
        vod_status = 0
        vod_remarks = ''                # 备注

        vod_pubdate = info.get('release', '')                # 上映日期

        vod_duration = info.get('duration', 0)  # 时长

        vod_lang = info.get('lang', '')  # 语言

        vod_areas = info.get('area', '').replace('|', '')
        vod_area = re.split('\d+', vod_areas)
        vod_area = ''.join(vod_area)[:-1]

        video_kinds = info.get('kind', '').replace('|', '')
        video_kind = re.split('\d+', video_kinds)
        vod_tag = ''.join(video_kind)[:-1]
        vod_tv = ''
        vod_weekday = ''

        vod_year = vod_pubdate.split('-')[0]
        vod_version = ''
        vod_sub = ''
        vod_en = ''
        vod_weekday = ''
        vod_tv = ''

        vod_director = ''
        vod_writer = ''
        vod_behind = ''
        vod_blurb = ''

        vod_actor = old_meta.get('vod_actor')
        vod_state = old_meta.get('vod_state')
        vod_mango_albumId = old_meta.get('vod_mango_albumId')
        vod_is_pay_mark = old_meta.get('vod_is_pay_mark')
        type_pid = old_meta.get('type_pid')
        vod_is_advance = old_meta.get('vod_is_advance')
        type_id = old_meta.get('type_id')
        vod_name = old_meta.get('vod_name')

        vod_pic_slide = ''
        vod_pic_thumb = ''


        video_id = info.get('video_id')
        video_url = info.get('video_url')

        vod_details = json.dumps(jjson, ensure_ascii=False).replace(r'\n', '').replace(r'\r', '').\
            replace('\\"', '').replace("'", '').replace('\\', '')                # 爬取数据
        tx_item = Tx_vod()
        tx_item['type_pid'] = type_pid
        tx_item['type_id'] = type_id
        tx_item['vod_name'] = vod_name
        tx_item['vod_mango_albumId'] = vod_mango_albumId
        tx_item['vod_pic'] = old_meta.get('vod_pic')
        tx_item['vod_pic_thumb'] = vod_pic_thumb
        tx_item['vod_pic_slide'] = vod_pic_slide
        tx_item['vod_tv'] = vod_tv
        tx_item['vod_weekday'] = vod_weekday
        tx_item['vod_area'] = vod_area
        tx_item['vod_version'] = vod_version
        tx_item['vod_state'] = vod_state
        tx_item['vod_is_pay_mark'] = vod_is_pay_mark
        tx_item['vod_is_advance'] = vod_is_advance
        tx_item['vod_isend'] = vod_isend
        tx_item['vod_serial'] = vod_serial
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
        first_url = old_meta.get('first_url')
        meta = {'tx_item': tx_item, 'selenium': 1}
        # yield Request(url=first_url, callback=self.parse3, meta=meta)
        vid = first_url.split('/')[-1].split('.')[0]
        cid = first_url.split('/')[-2]
        url = f'https://pcweb.api.mgtv.com/video/info?vid={vid}&cid={cid}'
        meta = {'tx_item': tx_item, 'first_video_id': old_meta.get('first_video_id'),
                'first_url': old_meta.get('first_url'), 'vid': vid, 'cid': cid}
        yield Request(url=url, callback=self.parse4, meta=meta)

    def parse3(self, response):
        tx_item = response.meta.get('tx_item')
        html = etree.HTML(response.text)
        try:
            vod_blurb = html.xpath('//div[@class="m-collection-wrap clearfix"]/div[@class="content"]/div[@class="introduce"]/p/text()')[0]
        except IndexError as e:
            vod_blurb = ''
        vod_director_areas = html.xpath('//div[@class="m-collection-wrap clearfix"]/div[@class="content"]/div[@class="introduce-items"]/p[@class="introduce-item"]')
        vod_director = ''
        vod_tv = ''
        vod_area = ''
        for vod_directorr in vod_director_areas:
            vv = vod_directorr.xpath('text()')[0]
            if "导演" in vv:
                vod_director = vod_directorr.xpath('a/text()')[0]
            elif "地区" in vv:
                vod_area = vod_directorr.xpath('a/text()')[0]
            elif "播出" in vv:
                vod_tv = vod_directorr.xpath('a/text()')[0]

        vod_tags = html.xpath(
            '//div[@class="m-collection-wrap clearfix"]/div[@class="content"]/div[@class="introduce-items"]/p[@class="introduce-item leader"]')

        vod_tag = ''
        for vod_tagg in vod_tags:
            vv = vod_tagg.xpath('text()')[0]
            if "类型" in vv:
                vod_tag = vod_tagg.xpath('a/text()')[0]

        vod_director = vod_director.rstrip().replace('/', ',')
        vod_tag = vod_tag.rstrip().replace('/', ',')
        vod_area = vod_area.rstrip().replace('/', ',')
        vod_tv = vod_tv.rstrip().replace('/', ',')

        tx_item['vod_area'] = vod_area
        tx_item['vod_director'] = vod_director
        tx_item['vod_tag'] = vod_tag
        tx_item['vod_tv'] = vod_tv
        tx_item['vod_blurb'] = vod_blurb

        yield tx_item


    def parse4(self, response):

        tx_item = response.meta.get('tx_item')
        jjson = json.loads(response.text)
        data = jjson.get('data', {})
        info = data.get('info', {})
        detail = info.get('detail', {})
        vod_area = detail.get('area', '').rstrip().replace('/', ',')
        vod_director = detail.get('director', '').rstrip().replace('/', ',')
        vod_tag = detail.get('kind', '').rstrip().replace('/', ',')
        vod_tv = detail.get('television', '').rstrip().replace('/', ',')
        vod_blurb = detail.get('story').replace(r'\n', '').replace(r'\r', '').\
            replace('\\"', '').replace("'", '').replace('\\', '')                # 爬取数据

        vod_pubdate = detail.get('releaseTime')
        try:
            vod_year = vod_pubdate.split('-')[0]
        except IndexError:
            vod_year = None

        tx_item['vod_area'] = vod_area
        tx_item['vod_director'] = vod_director
        tx_item['vod_tag'] = vod_tag
        tx_item['vod_tv'] = vod_tv
        tx_item['vod_blurb'] = vod_blurb
        if vod_pubdate:
            tx_item['vod_pubdate'] = vod_pubdate
        if vod_year:
            tx_item['vod_year'] = vod_year
        yield tx_item
        type_pid = tx_item['type_pid']
        if type_pid in ['3', '23']:
            url = f'https://pcweb.api.mgtv.com/list/master?_support=10000000&filterpre=true&vid={response.meta.get("vid")}&cid={response.meta.get("cid")}&pn=1&ps=60'
        else:
            url = f'https://pcweb.api.mgtv.com/episode/list?_support=10000000&version=5.5.35&video_id={response.meta.get("first_video_id")}&page=0&size=30'
        yield Request(url=url, callback=self.collection_crawl, meta={'tx_item': tx_item, 'first_url': response.meta.get("first_url"),
                                                                     'vid': response.meta.get("vid"), 'cid': response.meta.get("cid"), })

    def collection_crawl(self, response):
        tx_item = response.meta.get('tx_item')
        data = json.loads(response.text).get('data', {})
        lists = data.get('list', {})
        vod_id = 0
        vod_name = tx_item['vod_name']
        vod_is_from = tx_item['vod_is_from']
        type_pid = tx_item['type_pid']
        vod_mango_albumId = tx_item['vod_mango_albumId']

        if type_pid in ['2', '4', '3', '23']:
            for lis in lists:
                albumId = lis.get('video_id', '')
                collection = lis.get('t4')[1: -1]

                if not collection.isdigit():
                    collection = 0
                collection_title = lis.get('t1', '')
                collection_url = 'https://www.mgtv.com' + lis.get('url', '')
                collection_type = 0

                fonts = lis.get('corner', {})
                if fonts:
                    font = fonts[0].get('font')
                    if font == 'VIP':
                        collection_is_pay_mark = 1
                        collection_is_advance = 0
                        collection_is_state = 1
                    elif font == '超前点播':
                        collection_is_pay_mark = 1
                        collection_is_advance = 1
                        collection_is_state = 1

                    elif font == '预告':
                        collection_is_pay_mark = 0
                        collection_is_advance = 0
                        collection_is_state = 2
                    else:
                        collection_is_pay_mark = 0
                        collection_is_advance = 0
                        collection_is_state = 1
                else:
                    collection_is_pay_mark = 0
                    collection_is_advance = 0
                    collection_is_state = 1
                collection_weight = 0

                collection_last_time = ''
                collection_time_add = time.time()
                collection_time_up = time.time()
                collection_status = 0
                collection_details = json.dumps(lis).replace(r'\n', '').replace(r'\r', '').\
            replace('\\"', '').replace("'", '').replace('\\', '')                # 爬取数据

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
                tx_vod_collection_item['collection_details'] = collection_details
                tx_vod_collection_item['collection_time_add'] = collection_time_add
                tx_vod_collection_item['collection_time_up'] = collection_time_up
                tx_vod_collection_item['collection_status'] = collection_status
                tx_vod_collection_item['vod_mango_albumId'] = vod_mango_albumId

                yield tx_vod_collection_item
            if lists:
                last_collect = lists[-1]
                first_collect = lists[0]
                next_id = last_collect.get('next_id', '0')
                first_id = first_collect.get('video_id', 0)
                if next_id != '0':
                    urls = response.url.split(f'video_id={first_id}')
                    if len(urls) == 2:
                        next_url = urls[0] + 'video_id=' + next_id + urls[1]
                        yield Request(url=next_url, callback=self.collection_crawl, meta={'tx_item': tx_item})

        elif type_pid in ['1']:
            info = data.get('info')
            albumId = info.get('video_id', '')
            collection = 1
            collection_title = info.get('title', '')
            uurl = info.get('url')
            if uurl:
                collection_url = 'https://www.mgtv.com' + uurl
                collection_is_state = 1
            else:
                collection_url = response.meta.get("first_url")
                collection_is_state = 2
            collection_type = 0
            collection_is_pay_mark = info.get('isvip', 0)
            collection_is_advance = 0
            collection_weight = 0
            collection_last_time = ''
            collection_time_add = time.time()
            collection_time_up = time.time()
            collection_status = 0
            collection_details = json.dumps(info).replace(r'\n', '').replace(r'\r', ''). \
                replace('\\"', '').replace("'", '').replace('\\', '')  # 爬取数据

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
            tx_vod_collection_item['collection_details'] = collection_details
            tx_vod_collection_item['collection_time_add'] = collection_time_add
            tx_vod_collection_item['collection_time_up'] = collection_time_up
            tx_vod_collection_item['collection_status'] = collection_status
            tx_vod_collection_item['vod_mango_albumId'] = vod_mango_albumId

            yield tx_vod_collection_item




















