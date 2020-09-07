from collections import OrderedDict

channel_ids = OrderedDict({
    '1': {'channel_id': 3, 'a1': {'7': 176, '8': 175, '6': 177, '9': 178, '10': 43, '12': 44}},   # 电影在1后边多个b代表资费
    '2': {'channel_id': 2, 'a1': {'13': 10, '14': 12, '15': 11, '24': 193}},
    '23': {'channel_id': 51},                 # https://list.mgtv.com/-------------.html?channelId=51
    '4': {'channel_id': 50, 'a1': {'19': 52, '22': 53}},
    '3': {'channel_id': 1, 'a1': {'25': 1, '26': 2}},
    # '5': {'channel_id': 25, 'three_category_id': {'0': ''}},
})

urls = []
for type_pid, v in channel_ids.items():
    channel_id = v.get('channel_id')

    for type_id, vv in v.get('a1', {}).items():
        if vv in []:
            continue

        if channel_id in [3, 4]:
            url = f'https://list.mgtv.com/{channel_id}/{vv}--------a1-c2-1--a1-.html?channelId={channel_id}'
        else:
            url = f'https://list.mgtv.com/{channel_id}/a1-{vv}--------c2-1---.html?channelId={channel_id}'  # -的个数不读会影响结果一共13个
        urls.append(url)



#
# url = 'https://list.mgtv.com/50/a1-53---------c2-1---.html?channelId=50'
# # url = 'https://list.mgtv.com/50/a1-52---------c2-1---.html?channelId=50'
#
# import requests
# session = requests.session()
# headers = {
# # ':authority': 'list.mgtv.com',
# # ':method': 'GET',
# # ':path': '/50/a1-52-------a1-c2-1---.html?channelId=50',
# # ':scheme': 'https',
# 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
# 'accept-encoding': 'gzip, deflate, br',
# 'accept-language': 'zh-CN,zh;q=0.9',
# 'cookie': '_source_=A; __STKUUID=4e2f74e5-7615-4c0c-b077-13d0fc202f7a; PLANB_FREQUENCY=X078zMOjtQ_xbGBp; MQGUID=1300976636874899456; __MQGUID=1300976636874899456; mba_deviceid=2fd1b38a-f669-2556-4202-2365fc92c98c; mba_sessionid=bd16354f-157d-64ae-07e7-38915850e544; mba_cxid_expiration=1599062400000; mba_cxid=8kpqp21m4cm; sessionid=1599012046319_8kpqp21m4cm; pc_v6=v6; __random_seed=0.2831948753706812; PM_CHKID=4ec1d25399e6a598; mgtvlist_did=29efa8c6-be5f-40f3-85bb-e8b2e1d3efbe; mba_last_action_time=1599016691189; lastActionTime=1599016691346; beta_timer=1599016692555',
# 'referer': 'https://list.mgtv.com/50/a1--------a1-c2-1---.html?channelId=50',
# 'sec-fetch-dest': 'document',
# 'sec-fetch-mode': 'navigate',
# 'sec-fetch-site': 'same-origin',
# 'sec-fetch-user': '?1',
# 'upgrade-insecure-requests': '1',
# 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}
# res = session.get(url, headers=headers)
# # print(res.text)
# # res = session.get(url1)
# # print(res.text)




