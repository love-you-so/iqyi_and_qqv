
url = {
    "还可以搜": "https://pcw-api.iqiyi.com/search/search/queryword?cid=4&from=pcw_list"
}


channel_id = {
    '电影': {'channel_id': 1, 'three_category_id': {'喜剧片': 8, '爱情片': 6, '动作片': 11, '科幻': 9, '恐怖片': 10, '战争片': 7}},
    '电视剧': {'channel_id': 2, 'three_category_id': {'国产剧': 15, '港剧': 16, '台剧': 1117, '韩剧': 17, '日剧': 309, '美剧': 18, '英国剧': 28916, '泰国剧': 1114}},
    '纪录片': {'channel_id': 3},
    '动漫': {'channel_id': 4, 'three_category_id': {'国产': 37, '韩': 1106, '日': 38, '欧美': 30281}},
    '综艺': {'channel_id': 6, 'three_category_id': {'内地': 151, '韩': 33306, '港台': 152, '欧美': 154}},
    '资讯': {'channel_id': 25},
}


three_category_id = {
    1: 15,
    '港台': 16,
    '韩国': 17,
    '美剧': 18,
    '日本': 309,
    '泰国': 1114,
    '台湾': 1117,
    '英国': 28916,
    '其他': 19
}


headers = {
    'Accept': '*/*',
    'Access-Control-Allow-Credentials': 'true',
    'Cache-Control': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Content-Encoding': 'gzip',
    # 'Cookie': 'gzip',
    'DNT': '1',
    'Host': 'pcw-api.iqiyi.com',
    'Origin': 'http://list.iqiyi.com',
    'Content-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded;',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Referer': 'http://list.iqiyi.com/www/2/-------------11-1-1-iqiyi--.html',
    'Upgrade-Insecure-Requests': '1'
}


channel_ids = {
    '1': {'channel_id': 1, 'three_category_id': {'7': 8, '8': 6, '6': 11, '9': 9, '10': 10, '12': 7}},
    '2': {'channel_id': 2, 'three_category_id': {'13': 15, '14': [16, 1117], '15': [17, 309], '16': [18, 28916], '24': 1114}},
    '23': {'channel_id': 3, 'three_category_id':{'0': [20323, 20324]}},
    '4': {'channel_id': 4, 'three_category_id': {'19': 37, '20': [1106,  38], '22': 30281}},
    '3': {'channel_id': 6, 'three_category_id': {'25': 151, '27': 33306, '26': 152, '28': 154}},
    '5': {'channel_id': 25, 'three_category_id': {'0': ''}},
}

if __name__ == '__main__':

    url = 'https://pcw-api.iqiyi.com/search/recommend/list?channel_id=1&data_type=1&mode=24&page_id=1&ret_num=48&three_category_id=8'


    '''
    albumId: 6857415019905501
    categories: ["内地", "都市", "普通话"]
    channelId: 2
    description: "该剧以逗趣夫妻的婚后生活为主线，讲述了奶爸赵阳光联合岳母，与妻子白灿烂斗智斗法的故事。"
    exclusive: 0
    focus: "宋佳袁弘因娃开战"
    imageUrl: "http://pic7.iqiyipic.com/image/20200811/bd/06/a_100418311_m_601_m7.jpg"
    isAdvance: false
    latestOrder: 4
    name: "生活像阳光一样灿烂"
    payMark: 1
    payMarkUrl: "http://pic0.iqiyipic.com/common/20171106/ac/1b/vip_100000_v_601.png"
    people: {,…}
        main_charactor: [{id: 215344405, name: "宋佳"}, {id: 214697405, name: "袁弘"}, {id: 215241805, name: "刘芸"}]
    1: {id: 214697405, name: "袁弘"}
    2: {id: 215241805, name: "刘芸"}
    period: "2020-08-10"
    pingback: {doc_id: 6857415019905501}
    playUrl: "http://www.iqiyi.com/v_yxilco1zho.html"
    qiyiProduced: 0
    score: 7.9
    sourceId: 0
    title: "生活像阳光一样灿烂"
    videoCount: 40
    '''





















