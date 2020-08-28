# coding: utf8
import json
import re
import time
import requests
import pprint
import traceback
# from mian_db import Save
# from proxy import Proxy
# from iqyi.mian_db import Save
from tools.mian_db import Save
from tools.proxy import Proxy
from settings import channel_ids, headers
DEBUG = False  # 是否抛出异常  ，为了保证出现异常时不使整个程序停止


def debug(e):
    if DEBUG == True:
        raise e
    else:
        print(e)


class Crawl:

    def __init__(self):
        self.is_from = 2   # 来源 0:默认未标识来源  1:腾讯视频 2 爱奇艺 3 优酷 4 豆瓣 5bibi 6 芒果tv
        self.p = Proxy()

    def proxy(self):

        ip, id = self.p.get_proxy(1)
        if ip:
            return ip, id
        else:
            self.p.save_proxy(10)
            return self.proxy()

    def crawl(self, url, header=1):

        i = 0
        response = None
        while i<10:  # 如果下载失败重试三次
            ip, id = self.proxy()

            try:
                if header:
                    response = requests.get(url=url, headers=headers, proxies={'https': ip})
                else:
                    response = requests.get(url=url, proxies={'https': ip})
                break
            except Exception as e:
                debug(e)
                self.p.delete_proxy(id)
                # response = self.crawl(url, header=header)
                i += 1

        return response

    def parse(self, mode=24):
        for type_pid, v in channel_ids.items():
            if type_pid in ['']:
                continue
            channel_id = v.get('channel_id')
            three_category_ids = v.get('three_category_id')
            url = f'https://pcw-api.iqiyi.com/search/recommend/list?channel_id={channel_id}&data_type=1&mode={mode}&page_id=1&ret_num=48'

            if three_category_ids:
                for type_id, three_category_id in three_category_ids.items():
                    if isinstance(three_category_id, int):
                        url = url + '&three_category_id=%s' % three_category_id
                        for dic, albumId, playUrl in self.parse1(url, type_pid, type_id):
                            yield dic, albumId, playUrl, type_pid
                    elif isinstance(three_category_id, list):
                        for i in three_category_id:
                            url = url + '&three_category_id=%s' % i
                            for dic, albumId, playUrl in self.parse1(url, type_pid, type_id):
                                yield dic, albumId, playUrl, type_pid
                    elif isinstance(three_category_id, str):
                        for dic, albumId, playUrl in self.parse1(url, type_pid, type_id):
                            yield dic, albumId, playUrl, type_pid

    def parse1(self, url, type_pid, type_id):
        print('>>>>', url, type_pid, type_id)
        try:
            response = json.loads(self.crawl(url=url).text).get('data')

        except Exception as e:
            debug(e)
            response = {}
        print('<><><<><',response)
        has_next = response.get('has_next', 0)  # 是否有下一页
        lists = response.get('list', [])   # 视频信息列表（一页中的所有视频）
        type_dic = {'type_pid': type_pid, 'type_id': type_id}

        for album in lists:
            albumId_dic, albumId, playUrl = self._album(album)
            dic = self.tv(albumId)          # 爬取每个视频的全部信息
            dic.update(albumId_dic)
            dic.update(type_dic)
            yield dic, albumId, playUrl

        if has_next:  # 如果有下一页, 递归爬取下一页
            page = int(re.findall('\d+', re.findall(r'page_id=\d+&', url)[0])[0]) + 1
            url = re.split(r'page_id=\d+&', url)
            url = url[0] + f'page_id={page}&' + url[1]
            for dic, albumId, playUrl in self.parse1(url, type_pid, type_id):
                yield dic, albumId, playUrl

    def _album(self, album):
        '''
        获取视频albumId  唯一标识
        :param album:
        :return:
        '''
        # vod_name = album.get('name')   # 视频标题
        # vod_sub = album.get('')   # 视频副标题  !
        # vod_en = album.get('')   # 视频别名
        # vod_tag = album.get('')  # 视频标签
        # vod_pic = album.get('imageUrl')  # 视频图片
        # vod_pic_thumb = album.get('')  # 视频缩略图
        # vod_pic_slide = album.get('')  # 视频海报图
        # vod_actors = album.get('people').get('main_charactor')
        # vod_actor = ''          # 主演列表
        # for i in vod_actors:
        #     vod_actor += i.get('name')
        #     vod_actor += ';'

        # vod_director = album.get('')   # 导演
        # vod_writer = album.get('')   # 编剧
        # vod_behind = album.get('')   # 幕后
        # vod_blurb = album.get('description')    # 简介
        # vod_remarks = album.get('')  # 备注
        # vod_pubdate = album.get('')  # 上映日期
        # vod_total = album.get('videoCount')  # 总集数
        # vod_serial = album.get('latestOrder')  # 连载数
        # vod_tv = album.get('')  # 电视频道
        # vod_weekday = album.get('')   # 节目周期
        # vod_area = album.get('')   # 发行地区
        # vod_lang = album.get('')   # 对白语言
        # vod_year = album.get('')   # 上映年代
        # vod_version = album.get('')  # 影片版本
        # vod_state = album.get('')  # 资源类别 如：正片,预告片
        # vod_duration = album.get('duration')  # 时长

        # if vod_total == vod_serial:
        #     vod_isend = 1  # 是否完结
        # else:
        #     vod_isend = 0  # 是否完结

        # vod_time_add = album.get('')  # 添加时间
        # vod_time_up = album.get('')   # 更新时间
        # vod_is_from = 2   # 来源 0:默认未标识来源  1:腾讯视频 2 爱奇艺 3 优酷 4 豆瓣 5bibi 6 芒果tv
        # vod_is_advance = album.get('isAdvance')  # 是否超前点播
        # vod_is_pay_mark = album.get('payMark')  # 是否为vip
        vod_douban_albumId = album.get('')   # 目标视频关键id
        vod_tx_albumId = album.get('')   # 目标视频关键id
        vod_iqiyi_albumId = album.get('albumId')   # 目标视频关键id
        vod_yk_albumId = album.get('')   # 目标视频关键id
        # vod_status = album.get('')   # 视频状态 0等待自动检测 1 正常 2 下线
        # vod_details = album.get('')  # 爬取数据 详情  json格式
        dic = {
            'vod_douban_albumId': vod_douban_albumId,
            'vod_tx_albumId': vod_tx_albumId,
            'vod_iqiyi_albumId': vod_iqiyi_albumId,
            'vod_yk_albumId': vod_yk_albumId,
        }
        playUrl = album.get('playUrl')

        return dic, vod_iqiyi_albumId, playUrl

    def dic_to_str(self, dics, subType=None):
        if dics:
            s = ''          # 导演列表
            for i in dics:
                if isinstance(i, dict):

                    if subType or subType == 0:
                        if i.get('subType') == subType:
                            s += i.get('name')
                            s += ','
                    else:
                        s += i.get('name')
                        s += ','

                else:
                    s = i
        else:
            s = None
        if s:
            if s.endswith(','):
                s = s[:-1]
        return s

    def tv(self, albumId):
        '''
        获取视频全部信息
        :param albumId:
        :return:
        '''
        url = f'https://pcw-api.iqiyi.com/video/video/videoinfowithuser/{albumId}?agent_type=1&authcookie=&subkey={albumId}&subscribe=1'
        print('tv url>>>>' + url)
        response = self.crawl(url=url).text
        album = json.loads(response).get('data')

        vod_name = album.get('name')  # 视频标题
        vod_sub = album.get('subtitle')   # 视频副标题 data
        vod_en = album.get('')   # 视频别名
        vod_tags = album.get('categories')  # 视频标签
        vod_tag = self.dic_to_str(vod_tags, subType=2)
        vod_area = self.dic_to_str(vod_tags, subType=1)  # 发行地区
        vod_lang = self.dic_to_str(vod_tags, subType=0)  # 发行地区
        vod_pic = album.get('imageUrl')  # 视频图片
        vod_pic_thumb = album.get('')  # 视频缩略图
        vod_pic_slide = album.get('')  # 视频海报图
        try:
            vod_directors = album.get('people').get('director')
            vod_director = self.dic_to_str(vod_directors)  # 导演
        except AttributeError:
            vod_director = None
        try:
            vod_actors = album.get('people').get('main_charactor')
            vod_actor = self.dic_to_str(vod_actors)   # 主演
        except AttributeError:
            vod_actor = None
            # try:
            #     guest = album.get('peple').get('guest')
            #     vod_actor = self.dic_to_str(guest)
            # except AttributeError:
            #     vod_actor = None
            #
            # try:
            #     guest = album.get('peple').get('host')
            #     vod_actor = self.dic_to_str(guest)
            # except AttributeError:
            #     vod_actor = None

        try:
            vod_writers = album.get('people').get('screen_writer')
            vod_writer = self.dic_to_str(vod_writers)  # 编剧
        except AttributeError:
            vod_writer = None

        vod_behind = album.get('')   # 幕后

        vod_blurb = album.get('description')    # 简介
        if vod_blurb:
            vod_blurb = vod_blurb.replace("'", '').replace(r'\n', '').replace(r'\r', '').replace('\\"', '').replace("'", '').replace('\\', '')
        vod_remarks = album.get('')  # 备注

        vod_total = album.get('videoCount')  # 总集数
        vod_serial = album.get('latestOrder')  # 连载数

        # vod_pubdate = album.get('publishTime')  # 上映日期 改成日期
        vod_pubdate = album.get('period')  # 上映日期 改成日期
        vod_tv = album.get('television')  # 电视频道

        vod_weekday = album.get('')   # 节目周期

        # vod_areas = album.get('areas')
        # if vod_areas:
        #     vod_area = ''          # 发行地区
        #     for i in vod_areas:
        #         if isinstance(i, dict):
        #             vod_area += i.get('name')
        #             vod_area += ','
        #         else:
        #             vod_area = i
        # else:
        #     vod_area = album.get('')


        # vod_lang = album.get('')   # 对白语言

        vod_year = album.get('period')[:4]  # 上映年代
        vod_version = album.get('')  # 影片版本
        vod_state = album.get('')  # 资源类别 如：正片,预告片
        vod_duration = album.get('duration')  # 时长

        if vod_total == vod_serial:
            vod_isend = 1  # 是否完结
        else:
            vod_isend = 0  # 是否完结

        vod_time_add = time.time()  # 添加时间, 第一次填入之后不应改变

        vod_time_up = time.time()   # 更新时间， 每次修改都更新

        vod_is_from = self.is_from   # 来源 0:默认未标识来源  1:腾讯视频 2 爱奇艺 3 优酷 4 豆瓣 5bibi 6 芒果tv
        isAdvance = album.get('isAdvance')  # 是否超前点播
        if isAdvance:
            vod_is_advance = 1
        else:
            vod_is_advance = 0

        payMark = album.get('payMark')  # 是否为vip
        if payMark:
            vod_is_pay_mark = 1
        else:
            vod_is_pay_mark = 0

        vod_status = 0   # 视频状态 0等待自动检测 1 正常 2 下线
        vod_details = response.replace(r'+\n', '').replace(r'\r', '').replace("'", '').replace('\\"', '').replace('\\', '')  # 爬取数据 详情  json格式  \ 在存入时会产生编码问题

        dic = {
            'vod_name': vod_name,
            'vod_sub': vod_sub,
            'vod_en': vod_en,
            'vod_tag': vod_tag,
            'vod_pic': vod_pic,
            'vod_pic_thumb': vod_pic_thumb,
            'vod_pic_slide': vod_pic_slide,
            'vod_actor': vod_actor,
            'vod_director': vod_director,
            'vod_writer': vod_writer,
            'vod_behind': vod_behind,
            'vod_blurb': vod_blurb,
            'vod_remarks': vod_remarks,
            'vod_pubdate': vod_pubdate,
            'vod_total': vod_total,
            'vod_serial': vod_serial,
            'vod_tv': vod_tv,
            'vod_weekday': vod_weekday,
            'vod_area': vod_area,
            'vod_lang': vod_lang,
            'vod_year': vod_year,
            'vod_version': vod_version,
            'vod_state': vod_state,
            'vod_duration': vod_duration,
            'vod_isend': vod_isend,
            'vod_time_add': vod_time_add,
            'vod_time_up': vod_time_up,
            'vod_is_from': vod_is_from,
            'vod_is_advance': vod_is_advance,
            'vod_is_pay_mark': vod_is_pay_mark,
            'vod_status': vod_status,
            'vod_details': vod_details,
        }

        return dic

    def collect(self, albumId, vod_id, vod_name, type_pid):
        try:
            if type_pid in ['2', '4', '23']:
                url = f'https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={albumId}&page=1&size=30'
                print('单集路由>>>', url)
                response = self.crawl(url=url)
                # 电视剧、动漫、纪录片
                response = response.text
                data = json.loads(response).get('data', {})
                vod_id = vod_id  # 视频表自增id
                collect_lis = []
                epsodelist = data.get('epsodelist', [])  # 所有正片
                epsodelis = self.collect_dict(epsodelist, response=response, collection_is_state=1, vod_id=vod_id, vod_name=vod_name)
                updateprevuelist = data.get('updateprevuelist', [])  # 所有非vip预告片
                updateprevuelis = self.collect_dict(updateprevuelist, response=response, collection_is_state=0,
                                                    vod_id=vod_id, vod_name=vod_name)
                vipprevuelist = data.get('vipprevuelist', [])  # 所有vip预告
                vipprevuelis = self.collect_dict(vipprevuelist, response=response, collection_is_state=0, vod_id=vod_id, vod_name=vod_name)
                collect_lis.extend(epsodelis)
                collect_lis.extend(updateprevuelis)
                collect_lis.extend(vipprevuelis)

            elif type_pid in ['1', '5']:
                url = f'https://pcw-api.iqiyi.com/video/video/baseinfo/{albumId}'
                print('单集路由>>>', url)
                response = self.crawl(url=url)
                response = response.text
                data = json.loads(response).get('data')
                collect_lis = self.collect_dict([data], response=response, collection_is_state=1, vod_id=vod_id, vod_name=vod_name)
            else:
                url = f'https://pcw-api.iqiyi.com/video/video/baseinfo/{albumId}'
                print('单集路由>>>', url)
                response = self.crawl(url=url)
                response = response.text
                data = json.loads(response).get('data', {})
                albumUrl = data.get('albumUrl')
                Html = self.crawl(url=albumUrl, header=0)
                from lxml import etree
                html = etree.HTML(Html.text)
                try:
                    year = html.xpath('//input[@id="album-latest"]/@value')[0]
                except IndexError:
                    year = 'all'
                url = f'http://pcw-api.iqiyi.com/album/source/svlistinfo?cid=6&sourceid={albumId}&timelist={year}'
                response1 = self.crawl(url=url)

                collect_lis = []
                for i in json.loads(response1.text).get('data', {}).values():

                    collect_list = self.collect_dict(collect_lis=i, response=response1.text, collection_is_state=1, vod_id=vod_id, vod_name=vod_name)
                    collect_lis.extend(collect_list)
        except Exception as e:
            debug(e)
            collect_lis = []
        for collect_li in collect_lis:
            yield collect_li

    def collect_dict(self, collect_lis: list, response, collection_is_state, vod_id, vod_name):
        lis = []
        for collec in collect_lis:
            vod_name = vod_name  # 视频名称
            albumId = collec.get('tvId')  # 目标视频集关键id
            collection = collec.get('order', 1)  # 集
            # collection_title = collec.get('shortTitle')  # 标题
            collection_title = collec.get('name')  # 视频名称
            if not collection_title:
                collection_title = collec.get('albumName')  # 视频名称
            collection_url = collec.get('playUrl')  # 播放地址
            collection_type = collec.get('', 0)  # 1 标清 2 高清 3超清 4 蓝光 5 4k
            isAdvance = collec.get('isAdvance')  # 是否超前点播

            if isAdvance:
                vod_is_advance = 1
            else:
                vod_is_advance = 0
            collection_is_pay_mark = collec.get('payMark')  # 是否为vip
            if collection_is_pay_mark:
                collection_is_pay_mark = 1
            else:
                collection_is_pay_mark = 0

            collection_is_state = collection_is_state  # 资源类型 1 正片 2 预告片
            collection_weight = collec.get('', 0)  # 权重 优先级
            collection_last_time = collec.get('period')  # 最后更新时间
            collection_details = json.dumps(collec, ensure_ascii=False).replace(r'\n', '').replace(r'\r', '').replace('\\"', '').replace("'", '').replace('\\', '')  # 爬取页面数据 详情json
            collection_time_add = time.time()  # 添加时间
            collection_time_up = time.time()  # 更新时间
            collection_status = collec.get('', 0)  # 视频状态 0等待自动检测 1 正常 2 下线
            lis.append({
                'vod_id': vod_id,
                'vod_name': vod_name,
                'vod_is_from': self.is_from,
                'albumId': albumId,
                'collection': collection,
                'collection_title': collection_title,
                'collection_url': collection_url,
                'collection_type': collection_type,
                'collection_is_advance': vod_is_advance,
                'collection_is_pay_mark': collection_is_pay_mark,
                'collection_is_state': collection_is_state,
                'collection_weight': collection_weight,
                'collection_last_time': collection_last_time,
                'collection_details': collection_details,
                'collection_time_add': collection_time_add,
                'collection_time_up': collection_time_up,
                'collection_status': collection_status,
            })
        return lis


def main(mode=24):
    c = Crawl()
    mysqll = Save()
    try:
        for dic, albumId, playUrl, type_pid in c.parse(mode=mode):
            where = f'vod_iqiyi_albumId={albumId} or vod_douban_albumId={albumId} or vod_yk_albumId={albumId} or vod_tx_albumId={albumId}'
            try:
                vod_details = dic.pop('vod_details')
                vod_id, vod_name = mysqll.save(dic, 'tx_vod',  where, 'vod_iqiyi_albumId',)
                mysqll.save({'vod_id': vod_id, 'vod_details': vod_details}, table='tx_vod_json')
                # collect_lis = c.collect(albumId=albumId, vod_id=vod_id, type_pid=type_pid, vod_name=vod_name)
                collect_lis = []
                for collect_li in collect_lis:
                    pprint.pprint(collect_li)
                    where = f'albumId={collect_li.get("albumId")}'
                    collection_details = collect_li.pop('collection_details')
                    collection_id, vod_name = mysqll.save(collect_li, 'tx_vod_collection', where, 'albumId',)
                    mysqll.save({'collection_id': collection_id, 'collection_details': collection_details}, table='tx_vod_collection_json')
            except UnicodeEncodeError as e:
                debug(e)
            except Exception as e:
                debug(e)
                error = traceback.format_exc()
                mysqll.log(error)
    except Exception as e:
        debug(e)

    mysqll.close()


if __name__ == '__main__':
    import sys
    try:
        mode = sys.argv[1]
    except IndexError:
        mode = 24
    print(mode)
    main(mode=mode)
