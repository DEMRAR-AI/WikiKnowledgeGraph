import WebCrawler
# import N4J

if __name__ == '__main__':
    data = WebCrawler.crawl(3)
    print(data)
    WebCrawler.close_driver()