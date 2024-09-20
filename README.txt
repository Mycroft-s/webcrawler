Run the main function and the web crawler will start.
Console will print the staus of crawler, like currently crawling, fetched content from url, data size and some errors.
The crawler will create crawl_log.txt in local file, which records every url we have crawled.
Here is a sample: 
URL: http://example.com, Size: 1234 bytes, Status: 200, Depth: 2, Time: 2024-09-19 14:30:45

And if you want to get html information from each URL we crawled, you need to use the function named "save_content_to_file" in the utils.py, 
which can create a new file named crawled_pages and will save the crawled contents to a file with the named of URL.
It will be easily work, when you cancel "#" in  line 97 in main.py.

