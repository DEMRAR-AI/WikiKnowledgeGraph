from Scraper import Scraper

if __name__ == '__main__':
    scraper = Scraper()
    scraper.process(depth=2)
    nodes = scraper.get_nodes()
    scraper.display_stats()
    scraper.push_data(clear=True)
    scraper.close()
    print(nodes)

