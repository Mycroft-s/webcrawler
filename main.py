import threading
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fetcher import fetch_url
from parser import parse_links
from utils import log_url_info, is_nz_domain, get_mime_type, save_content_to_file, is_blacklisted, save_seed_set_to_file
from robots_handler import can_fetch
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.parse import urlparse, urljoin
# 使用锁来保护共享资源
queue_lock = threading.Lock()
visited_lock = threading.Lock()


#url 标准化
def normalize_url(url):
    """去掉末尾的常见文件名，规范化URL"""
    parsed_url = urlparse(url)
    if parsed_url.path.endswith(('index.html', 'index.htm', 'index.php', 'index.jsp')):
        url = urljoin(url, '/')  # 去掉文件名部分
    return url

#Single Process
def bfs_crawl(seed_urls):
    visited_urls = set()
    queue = seed_urls
    depth_dict = {url: 0 for url in seed_urls}  # 记录每个URL的爬取深度

    while queue:
        url = queue.pop(0)
        print(f"Currently crawling: {url}")
        if url in visited_urls:
            continue

        if not can_fetch(url):
            print(f"Blocked by robots.txt: {url}")
            log_url_info(url, 0, 'Blocked by robots.txt', depth_dict[url])
            continue

        visited_urls.add(url)
        depth = depth_dict[url]

        try:
            content, final_url, status_code = fetch_url(url)
            if content:
                print(f"Fetched content from {url}, size: {len(content)} bytes")
                #save_content_to_file(url, content)
                log_url_info(url, len(content), status_code, depth)
                # 解析链接
                links = parse_links(content, url)
                print(f"Found {len(links)} links on {url}")

                # 处理每个链接时加入更多错误处理
                for link in links[:100]:
                    if link not in visited_urls and is_nz_domain(link):
                        #print(link)
                        mime_type = get_mime_type(link)
                        if mime_type == 'text/html':
                            queue.append(link)  #end  bfs
                            #queue.insert(0,link) #front  dfs
                            depth_dict[link] = depth + 1
            else:
                log_url_info(url, 0, status_code, depth, "Failed to fetch content")
        except HTTPError as e:
            print(f"HTTP error accessing {url}: {e}")
        except URLError as e:
            print(f"URL error accessing {url}: {e}")
            log_url_info(url, 0, 'Error', depth)
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            log_url_info(url, 0, 'Error', depth)

# load URL and consist randomly
def load_random_seed_urls(filename, n=20):
    """从文件中加载种子URL，并随机选择两个不同的种子集合"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            seed_urls = [line.strip() for line in f.readlines() if line.strip()]
        # 随机选择两个集合，每个集合 20 个种子
        random.shuffle(seed_urls)
        seed_set_1 = seed_urls[:n]
        seed_set_2 = seed_urls[n:2*n]
        return seed_set_1, seed_set_2
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return [], []


#Single Process
def crawl_url(url, depth, visited_urls, depth_dict, queue, log_filename):
    global pages_crawled, total_size, error_404_count
    """处理单个 URL 的爬虫任务"""
    print(f"Currently crawling: {url}")

    # 检查 robots.txt
    if not can_fetch(url):
        print(f"Blocked by robots.txt: {url}")
        log_url_info(url, 0, 'Blocked by robots.txt', depth, log_filename)
        return

    try:
        content, final_url, status_code = fetch_url(url)
        if content:
            print(f"Fetched content from {url}, size: {len(content)} bytes")
            #save_content_to_file(url, content)
            log_url_info(url, len(content), status_code, depth, log_filename)

            # 解析链接
            links = parse_links(content, url)
            print(f"Found {len(links)} links on {url}")
            # 批量将所有链接加入队列，不在此处处理详细逻辑
            with queue_lock:
                queue.extend(links)  # 将所有链接批量加入队列
                # 使用字典推导式一次性更新新链接的深度
                depth_dict.update({link: depth + 1 for link in links})
        else:
            log_url_info(url, 0, status_code, depth, "Failed to fetch content")
    except HTTPError as e:
        print(f"HTTP error accessing {url}: {e}")
    except URLError as e:
        print(f"URL error accessing {url}: {e}")
        log_url_info(url, 0, 'Error', depth, log_filename)
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        log_url_info(url, 0, 'Error', depth, log_filename)

"""
            # 加锁，保护共享队列和 visited_urls
            with visited_lock:
                for link in links[:100]:
                    # 在加入 visited_urls 之前对URL进行规范化
                    normalized_url = normalize_url(link)
                    if normalized_url not in visited_urls and is_nz_domain(link):
                        mime_type = get_mime_type(link)
                        if not is_blacklisted(link) and mime_type == 'text/html':
                            with queue_lock:
                                queue.append(link)
                            depth_dict[link] = depth + 1
"""

#mulit-process
def bfs_crawl_multithreaded(seed_urls, log_filename, max_workers=5, max_pages=5000):
    visited_urls = set()
    queue = seed_urls
    depth_dict = {url: 0 for url in seed_urls}

    pages_crawled = 0
    total_size = 0
    error_404_count = 0
    start_time = time.time()

    # 创建线程池 create thread pool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        while queue and pages_crawled < max_pages:
            with queue_lock:
                url = queue.pop(0)

            # 规范化 URL 并进行后续处理  normalized
            normalized_url = normalize_url(url)

            with visited_lock:
                if normalized_url in visited_urls:
                    continue  # 如果已访问，则跳过
                visited_urls.add(normalized_url)  # 使用规范化后的 URL 记录

            # 检查域名、黑名单和 MIME 类型  check
            if not is_nz_domain(normalized_url) or is_blacklisted(normalized_url):
                continue

            mime_type = get_mime_type(normalized_url)
            if mime_type != 'text/html':
                continue

            # 提交任务到线程池 submit
            depth = depth_dict[url]
            future = executor.submit(crawl_url, normalized_url, depth, visited_urls, depth_dict, queue, log_filename)
            futures.append(future)

            pages_crawled += 1

        # 处理任务完成时的回调   callback
        for future in as_completed(futures):
            try:
                future.result()  # 获取线程的执行结果
            except Exception as e:
                print(f"Thread raised an exception: {e}")

    # 爬取结束，记录结束时间  record time
    end_time = time.time()
    total_time = end_time - start_time

    # 输出统计信息 print
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write("\n--- Crawl Statistics ---\n")
        log_file.write(f"Total pages crawled: {pages_crawled}\n")
        log_file.write(f"Total size of pages: {total_size} bytes\n")
        log_file.write(f"Total time taken: {total_time:.2f} seconds\n")
        log_file.write(f"404 errors encountered: {error_404_count}\n")


def main():
    # 从文件中加载两个随机种子集合
    seed_set_1, seed_set_2 = load_random_seed_urls('nz_domain_seeds_list.txt', n=20)
    # 保存 seed_set_1 和 seed_set_2 到文件
    save_seed_set_to_file(seed_set_1, 'seed_set_1.txt')
    save_seed_set_to_file(seed_set_2, 'seed_set_2.txt')

    if not seed_set_1 or not seed_set_2:
        print("No seed URLs found.")
        return

    #单线程爬虫
    #bfs_crawl(seed_urls)
    # 使用多线程版本的爬虫
    bfs_crawl_multithreaded(seed_set_1, log_filename='crawl_log_1.txt', max_workers=30)
    bfs_crawl_multithreaded(seed_set_2, log_filename='crawl_log_2.txt', max_workers=30)


if __name__ == "__main__":
    main()
