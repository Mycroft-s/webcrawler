from bs4 import BeautifulSoup  # 使用 BeautifulSoup 解析 HTML
from urllib.parse import urljoin  # 处理相对链接
import urllib.request  # 导入 urllib.request 来处理 HTTP 请求
import urllib.parse  # 导入 urllib.parse 来处理 URL 的拼接

def parse_links(content, base_url):
    """从HTML内容中提取链接"""
    soup = BeautifulSoup(content, 'html.parser')
    base_tag = soup.find('base', href=True)
    if base_tag:
        base_url = base_tag['href']  # 使用<base>标签指定的URL作为基础
    links = []
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        # 解析相对路径为绝对路径
        full_link = urllib.parse.urljoin(base_url, link)
        links.append(full_link)
    return links
