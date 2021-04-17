# 导入数据请求模块
import requests
from Tools.scripts.linktree import linknames

link = 'https://flk.npc.gov.cn/api/'
get_data = {
    'type':' flfg',
    'xlwj':' 02',
    'xlwj':' 03',
    'xlwj':' 04',
    'xlwj':' 05',
    'xlwj':' 06',
    'xlwj':' 07',
    'xlwj':' 08',
    'searchType':' title;vague',
    'sortTr':' f_bbrq_s;desc',
    'gbrqStart':' ',
    'gbrqEnd':' ',
    'sxrqStart':' ',
    'sxrqEnd':' ',
    'sort':' true',
    'page':' 1',
    'size':' 10',
    '_':' 1739589200132',
}
# 模拟浏览器 --> 请求头
headers = {
    # user-agent 表示浏览器基本身份信息
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
}
json_data = requests.get(url=link, params=get_data, headers=headers).json()
for content_id in json_data['result']['data']:
    """
    1.发送请求，模拟浏览器对url地址发送请求
        -请求链接
        -模拟浏览器 伪装
        -发送请示 --> 请求方式
    """
    # 请求链接
    url = 'https://flk.npc.gov.cn/api/detail'
    # 模拟浏览器 --> 请求头
    headers = {
        # user-agent 表示浏览器基本身份信息
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }
    # 请求参数
    data = {
        'id': content_id['id']
    }
    # 发送请求
    response = requests.post(url=url, data=data, headers=headers)
    """
    2.获取数据，获取服务器返回响应数据
        根据返回数据样子，获取相应的内容
    3.解析数据，提取我们想要的数据内容
        文档标题 / 文档下载地址
    """
    # 标题
    title = response.json()['result']['title']
    # 下载链接
    download_url = 'https://wb.flk.npc.gov.cn' + response.json()['result']['body'][0]['path']
    # 获取文件格式
    name = download_url.split('.')[-1]
    print(title, download_url)
    """
    4.保存数据，把文档保存到本地文件夹
        图片：xxx.jgp
        文档：xxx.docx
    """
    # 对于下载地址发送请求，获取文档数据
    content = requests.get(url=download_url, headers=headers).content
    with open('data\\' + title + '.' + name,mode='wb') as f:
        f.write(content)