
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
    # '5': {'channel_id': 25, 'three_category_id': {'0': '9999'}},
}



starts = {  # 爬取过滤      three_category_id中值的部分： 页码
    37: 33, 20324: 26, 20323: 76, 1114: 3, 1106: 1, 38: 5
}

















