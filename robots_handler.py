from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse

def can_fetch(url):
    """处理 robots.txt 协议，检查是否允许爬取"""
    rp = RobotFileParser()
    base_url = "{uri.scheme}://{uri.netloc}/".format(uri=urlparse(url))
    rp.set_url(urljoin(base_url, 'robots.txt'))
    try:
        rp.read()
        return rp.can_fetch('*', url)
    except Exception as e:
        print(f"Error reading robots.txt for {url}: {e}")
        return True  # 默认允许爬取
