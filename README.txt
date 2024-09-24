Project Name:  WebCrawler
GitHub：https://github.com/Mycroft-s/webcrawler
List of Submitted Files and Their Purpose:
1. main.py: The main program file that contains the multithreaded web crawling logic. It initializes the crawl and handles the URL queue.
2. fetcher.py: Handles downloading the webpage content from the given URL.
3. parser.py: Responsible for parsing the webpage content and extracting links.
4. robots_handler.py: Processes the robots.txt file to ensure the crawler does not access disallowed pages.
5. utils.py: Contains utility functions like logging, fetching MIME types, normalizing URLs, etc.
6. nz_domain_seeds_list.txt: A file containing a list of New Zealand domain URLs that serve as the seed URLs for the crawler.
7. seed_set_1.txt: The first randomly selected seed set file containing 20 URLs, generated from nz_domain_seeds_list.txt.
8. seed_set_2.txt: The second randomly selected seed set file containing 20 URLs, generated from nz_domain_seeds_list.txt.
9. crawl_log_1.txt: The log file that records all crawled pages and statistics for the first seed set.
10. crawl_log_2.txt: The log file that records all crawled pages and statistics for the second seed set.

How to Compile and Run the Program:
1. Install Dependencies: Ensure you have the following Python libraries installed:

bash
pip install requests beautifulsoup4 urllib3


2. Run the Program: To run the crawler, use Python3:

bash
python main.py

The program will randomly select two seed sets from nz_domain_seeds_list.txt, and run separate crawls for each set. The results will be saved in crawl_log_1.txt and crawl_log_2.txt.

3.Input Parameters:
nz_domain_seeds_list.txt: The file containing seed URLs.
The program uses 20 URLs as the initial seed set for each crawl.
The crawler will retrieve a maximum of 5000 pages for each run.

4.Configuration Files:
nz_domain_seeds_list.txt: This file contains a list of New Zealand domain URLs that serve as the initial seed URLs for the crawl.


Parameter Limitations:
Maximum pages to be crawled: 5000.
The program uses multithreading with a default limit of 30 threads, which can be adjusted with the max_workers parameter.


Run the main function and the web crawler will start.
Console will print the staus of crawler, like currently crawling, fetched content from url, data size and some errors.
The crawler will create crawl_log.txt in local file, which records every url we have crawled.
Here is a sample: 
URL: http://example.com, Size: 1234 bytes, Status: 200, Depth: 2, Time: 2024-09-19 14:30:45

And if you want to get html information from each URL we crawled, you need to use the function named "save_content_to_file" in the utils.py, 
which can create a new file named crawled_pages and will save the crawled contents to a file with the named of URL.


BUG:
Multithreading Resource Contention
Issue: Since I am using multithreading with ThreadPoolExecutor to crawl websites, I encountered issues with shared resources like queue and visited_urls. Without proper synchronization, these shared resources may lead to race conditions where multiple threads try to access or modify them at the same time. This could result in URLs being missed or data being corrupted.
Solution: I implemented queue_lock and visited_lock to protect these shared resources. However, I need to ensure that all critical sections, particularly those where queue and visited_urls are updated, are properly locked. This will prevent race conditions and ensure that all URLs are crawled correctly without being skipped.
404 Error Count Inaccuracy
Issue: I implemented error counting for 404 errors, but I encountered an issue where some 404 errors were not being accurately logged. To optimize the crawling process, I used a method to check the HTTP status code and skip sites that returned 404. However, this approach inadvertently caused a problem with error counting, as some 404 errors were being skipped without incrementing the error_404_count correctly.
Solution: I need to ensure that each time an HTTPError is caught in the crawl_url function, I check if the status code is 404 and properly increment the error_404_count before skipping those URLs. This will ensure that 404 errors are accurately tracked and logged during the crawling process.
