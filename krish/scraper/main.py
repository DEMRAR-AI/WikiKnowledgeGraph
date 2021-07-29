from Scraper import Scraper
from Refinery import Refinery
from threading import Thread
import concurrent.futures
from WikiKnowledgeGraph.ben.scraper.ezsender.main import Rabbit

if __name__ == '__main__':
    scraper = Scraper()
    refinery = Refinery(uri='bolt://localhost:7687', user='neo4j', password='abc123')
    scraper.process(2)
    nodes = scraper.get_nodes()
    scraper.display_stats()
    scraper.close()
    """
    refinery.push_to_cache('cache', nodes)
    refinery.push_to_db(nodes, clear=True)
    """
    print(nodes)
    rabbit = Rabbit()
    rabbit.connect()
    rabbit.send_dict(nodes)

