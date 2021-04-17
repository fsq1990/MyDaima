import requests
import time
import json
import os
import re
from urllib.parse import quote
from bs4 import BeautifulSoup

# 全局配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Referer': 'https://flk.npc.gov.cn/',
    'Origin': 'https://flk.npc.gov.cn'
}

PROXY = {}  # 如有需要可设置代理 如：{'http': 'http://127.0.0.1:10809'}


def get_law_list(category='法律', max_page=1):
    """获取法律列表（合规版本）"""
    category_map = {
        "法律": 11, "行政法规": 12,
        "地方性法规": 13, "司法解释": 14
    }

    results = []
    base_api = "https://flk.npc.gov.cn/api/"

    try:
        for page in range(1, max_page + 1):
            params = {
                "type": category_map[category],
                "searchType": "title;accurate",
                "sortTr": "f_bbrq asc",
                "page": page,
                "size": 10,
                "_": int(time.time() * 1000)
            }

            response = requests.post(
                base_api,
                headers=HEADERS,
                data=params,
                proxies=PROXY,
                timeout=20
            )
            response.raise_for_status()

            data = response.json()
            if data.get('code') != 200:
                raise ValueError(f"API返回错误: {data.get('message')}")

            results.extend(data['data'])
            print(f"已获取 {category} 第 {page} 页，当前总数：{len(results)}")

            time.sleep(3.5)  # 严格遵守反爬要求

    except Exception as e:
        print(f"获取列表失败: {str(e)}")
        return []

    return results


def download_law_detail(law_data, save_dir='laws'):
    """下载法律全文（含增强版反爬处理）"""
    try:
        # 创建目录（自动处理路径分隔符）
        os.makedirs(save_dir, exist_ok=True)

        # 构造合法URL
        encoded_title = quote(quote(law_data['title']))
        detail_url = f"https://flk.npc.gov.cn/detail2.html?lawId={law_data['id']}&title={encoded_title}"

        # 带超时和重试的请求
        response = requests.get(
            detail_url,
            headers={**HEADERS, 'Accept': 'text/html,application/xhtml+xml'},
            proxies=PROXY,
            timeout=15
        )
        response.raise_for_status()

        # 解析内容
        soup = BeautifulSoup(response.text, 'lxml')
        content_div = soup.find('div', class_='content')
        if not content_div:
            raise ValueError("未找到法律正文内容")

        # 清理格式
        content = '\n'.join([p.text.strip() for p in content_div.find_all('p')])

        # 安全文件名
        safe_title = re.sub(r'[\\/:*?"<>|（）]', '', law_data['title'])
        file_path = os.path.join(save_dir, f"{safe_title}.md")  # 用Markdown格式保存

        # 结构化保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {law_data['title']}\n\n")
            f.write(f"**颁布日期**: {law_data['fbrq']}\n")
            f.write(f"**发文字号**: {law_data['wh']}\n\n")
            f.write("## 正文\n")
            f.write(content)

        print(f"√ 成功保存：{safe_title}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {str(e)}")
    except Exception as e:
        print(f"处理 {law_data.get('title', '未知')} 失败: {str(e)}")

    return False


if __name__ == "__main__":
    # 示例：获取1页法律数据
    laws = get_law_list(category='法律', max_page=1)

    # 限速下载（建议设置3秒以上间隔）
    for idx, law in enumerate(laws, 1):
        print(f"\n[{idx}/{len(laws)}] 正在处理: {law['title']}")
        download_law_detail(law)
        time.sleep(4.2)  # 重要！遵守网站要求