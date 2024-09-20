import urllib.request
from bs4 import BeautifulSoup

def fetch_url(url, timeout=10):
    try:
        # 设置 User-Agent 模拟浏览器请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        # 使用 urllib 进行 HTTP 请求
        response = urllib.request.urlopen(req, timeout=timeout)
        # 获取最终重定向后的URL
        final_url = response.geturl()  # 这是处理重定向后的最终URL
        content = response.read().decode('utf-8')  # 读取网页内容并解码
        return content, final_url, response.getcode()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, url, None  # 出现错误时返回 None

def parse_links(content, base_url):
    # 使用 BeautifulSoup 解析链接
    soup = BeautifulSoup(content, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        absolute_url = urllib.parse.urljoin(base_url, link['href'])
        links.append(absolute_url)
    return links
