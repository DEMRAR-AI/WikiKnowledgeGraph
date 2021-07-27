from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from timeit import timeit
from threading import Thread
import concurrent.futures
from memory_profiler import profile
class Timer(object):
    def __init__(self):
        self.total_time = 0

    def add_time(self, time):
        self.total_time += time

    def get_avg_time(self, size):
        return self.total_time / size

    def get_total_time(self):
        return self.total_time

class Scraper(object):
    ROOT = '/wiki/Walt_Disney'
    DRIVER_PATH = 'C:\Program Files (x86)\chromedriver.exe'
    PREFIX = 'https://www.wikipedia.com'
    CASES = ['Special', 'Help', 'File', 'Talk', 'Wikipedia', 'cite', 'wikipedia', 'disambiguation', 'edit']

    def __init__(self):
        self.nodes = dict()
        self.driver = webdriver.Chrome(Scraper.DRIVER_PATH)
        self.timer = Timer()
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def get_nodes(self):
        return self.nodes

    def _contains(str):
        for case in Scraper.CASES:
            if case in str:
                return True
        return False and not '/wiki/' in str

    def clean_str(str):
        if '/wiki/' in str:
            str = str[str.find('i/') + 2:]
        str = str.replace('_', ' ')
        return str

    def _get_branch_nodes(self, pg):
        is_list = False
        if "List_of" in pg:
            is_list = True

        main_p = None
        a_tags = list()
        a_tag_dict = dict()
        self.driver.get(Scraper.PREFIX + pg)
        failure = list()
        if not is_list:
            ps = self.driver.find_elements_by_tag_name('p')
            for p in ps:
                try:
                    p.find_element_by_tag_name('b')
                    if len(p.find_elements_by_tag_name('a')) > 0:
                        main_p = p
                        break
                    else:
                        continue
                except NoSuchElementException:
                    temp = p.find_elements_by_tag_name('a')
                    for a in temp:
                        failure.append(a)
            if main_p == None:
                a_tags = failure
            # print(main_p.text)
            else:
                a_tags = main_p.find_elements_by_tag_name('a')

            for a_tag in a_tags:
                # print(a_tag.text)
                href = a_tag.get_attribute('href')
                href = href[href.find('g/') + 1:]
                if not Scraper._contains(href):
                    a_tag_dict[a_tag.text] = href
        else:
            try:
                table = self.driver.find_element_by_class_name('wikitable')
            except NoSuchElementException:
                table = self.driver.find_element_by_class_name("mw-headline")
            a_tags = table.find_elements_by_tag_name('a')
            for a_tag in a_tags:
                if a_tag:
                    href = a_tag.get_attribute('href')
                    href = href[href.find('g/') + 1:]
                    if not Scraper._contains(href):
                        a_tag_dict[a_tag.text] = href
                else:
                    continue
        return list(a_tag_dict.values())

    def process(self, depth=2, root=ROOT):
        if root == None or len(root) == 0:
            return
        if depth == 0:
            return
        """
        tts = timeit(lambda: self._get_branch_nodes(root), number=1)
        print(root, tts)
        self.timer.add_time(tts)
        """
        data = self._get_branch_nodes(root)
        self.nodes[root] = data
        """
        cache.write(root + '\n')
        cache.write(str(data) + '\n\n')
        """
        for dt in data:
            # self.executor.submit(self.process, (depth-1, dt))
            self.process(depth-1, dt)

    @profile
    def profile_process(self, depth):
        self.process(depth)

    def display_stats(self):
        print('TOTAL TIME:', self.timer.total_time)
        print('AVG TIME TO SCRAPE:', self.timer.get_avg_time(len(self.nodes.keys())))

    def close(self):
        self.driver.close()
