import time
from urllib.parse import urlparse  # 用于解析URL
import mimetypes
import urllib.request
from urllib.error import HTTPError, URLError
import socket


def log_url_info(url, size, status_code, depth, message=None):
    """记录URL访问日志信息，带有可选的message参数"""
    with open('crawl_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"URL: {url}, Size: {size} bytes, Status: {status_code}, Depth: {depth}, Time: {time.localtime(time.time())}\n")
        if message:
            log_file.write(f"Message: {message}\n")
        #log_file.write("\n")


def is_nz_domain(url):
    """检查是否为 .nz 域名"""
    return urlparse(url).netloc.endswith('.nz')


# 设置全局超时时间，防止卡住
socket.setdefaulttimeout(10)
blacklist_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp3', '.mp4', '.zip']

def is_blacklisted(url):
    """检查文件扩展名是否在黑名单中"""
    for ext in blacklist_extensions:
        if url.lower().endswith(ext):
            return True
    return False

def get_mime_type(url, retries=3):
    """获取文件的 MIME 类型，过滤非HTML文件"""
    mime_type, _ = mimetypes.guess_type(url)
    if mime_type is None:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            req = urllib.request.Request(url, headers=headers)

            # 重试机制，最多尝试指定次数
            for attempt in range(retries):
                try:
                    response = urllib.request.urlopen(req, timeout=10)
                    return response.info().get_content_type()
                except HTTPError as e:
                    if e.code == 404:
                        print(f"Page not found for {url}: {e}")
                        return None  # 跳过 404 页面
                    elif e.code in [403, 500]:
                        print(f"Server error for {url}: {e}")
                        return None  # 处理 403 和 500 错误
                    else:
                        print(f"HTTP error for {url}: {e}")
                        return None
                except URLError as e:
                    print(f"URL error for {url}: {e}")
                    continue  # 网络错误时重试
                except socket.timeout as e:
                    print(f"Timeout for {url}: {e}")
                    continue  # 超时错误时重试
            print(f"Max retries reached for {url}")
            return None  # 超过重试次数后跳过
        except Exception as e:
            print(f"General error getting MIME type for {url}: {e}")
            return None
    return mime_type


import os
import re

def save_content_to_file(url, content, output_dir='crawled_pages'):
    """将爬取到的内容保存到文件中"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 用URL生成合法的文件名
    filename = re.sub(r'\W+', '_', url)[:100]  # 将URL中的非法字符替换为下划线
    file_path = os.path.join(output_dir, f"{filename}.txt")

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved content from {url} to {file_path}")
    except Exception as e:
        print(f"Error saving content for {url}: {e}")
