from lxml import html
import requests
import queue
import threading
import time
from neomodel import StructuredNode, StringProperty, Relationship, config


def bin_search(arr, item):
    lower, upper = 0, len(arr) - 1
    while lower <= upper:
        middle = (lower + upper) // 2

        if arr[middle] == item:
            return middle

        if arr[middle] < item:
            lower = middle + 1
        elif arr[middle] > item:
            upper = middle - 1


class Basic(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    to = Relationship("Basic", "related_to")
    link = StringProperty(required=False)


def worker():
    while True:
        title, link_, depth, node_ = q.get()
        process_wiki(title, link_, depth, node_)


def process_wiki(title, site, depth, parent):
    global q
    this_node = Basic(name=title, link=site)
    this_node.save()
    if parent:
        this_node.to.connect(parent)

    if depth < 1:
        return

    page = requests.get(base + site)
    tree = html.fromstring(page.content)

    for el in tree.xpath(xpath):
        try:
            el.attrib['href']
        except KeyError:
            continue

        search = Basic.nodes.get_or_none(link=el.attrib['href'])

        if "/wiki/" == el.attrib['href'][:6] and ("BookSources" and "citation_needed" and "Citation_needed" and ":") \
                not in el.attrib['href'] and el.text_content():
            if search:
                this_node.to.connect(search)
            else:
                q.put((el.text_content(), el.attrib['href'], depth - 1, this_node))


if __name__ == '__main__':
    server = "bolt://neo4j:1234@localhost:7687"
    config.DATABASE_URL = server

    user = "neo4j"
    password = "1234"

    for x in Basic.nodes.all():
        print(x)
        x.delete()

    base = "https://en.wikipedia.org"
    link = "/wiki/Jarvis_Island/People"

    if link.count("/") > 2:
        link = "/".join(link.split("/")[:3])

    # with "see also part"
    xpath = '//div[@id="mw-content-text"]//p//a'

    q = queue.Queue()
    threads = []

    for _ in range(10):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    process_wiki(link.split("/")[2], link, 2, None)

    old = None
    while True:
        time.sleep(10)
        length = len(Basic.nodes.all())
        if length == old:
            exit()
        old = length
