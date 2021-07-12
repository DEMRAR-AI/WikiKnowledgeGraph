import queue
import bisect
import shelve
import threading
import time
import zlib

import requests
from ezsender.main import Rabbit
from lxml import html


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


def print_decompressed(d):
    print({zlib.decompress(key).decode("utf-8"): [zlib.decompress(x).decode("utf-8") for x in d[key]] for key in d})


def worker():
    global q, not_done
    try:
        while not_done:
            link_, depth_ = q.get(block=True, timeout=5)
            process_wiki(link_, depth_)
    except queue.Empty:
        print(links)
        return


def process_wiki(site, depth):
    global q, table
    if depth < 1:
        return

    # check if site is in compressed form or not
    if type(site) != str:
        site = zlib.decompress(site).decode("utf-8")

    # request information
    page = requests.get(base + site)
    tree = html.fromstring(page.content)

    store = []

    # iterate through all matched elements
    for el in tree.xpath(xpath):
        try:
            el.attrib['href']
        except KeyError:
            continue
        # cleans up link
        if el.attrib['href'].count("/") > 2:
            el.attrib['href'] = "/".join(link.split("/")[:3])
        if bin_search(links, site) == -1:
            if "/wiki/" == el.attrib['href'][:6] and ("BookSources" and "citation_needed" and "Citation_needed" and ":") \
                    not in el.attrib['href'] and el.text_content():

                # compresses data to be decompressed and read later
                bytes_href = bytes(el.attrib['href'], "utf-8")
                compressed = zlib.compress(bytes_href)

                # add to temp array the links being processed
                store.append(compressed)
                # add to queue the next link to be processed
                q.put((el.attrib['href'], depth - 1))

    # write to table with the compressed key and compressed text within array
    table[zlib.compress(bytes(site, "utf-8"))] = store

    # insert sorted into links for easier and more efficient searching down the line
    bisect.insort(processed, site)
    bisect.insort(links, site)


if __name__ == '__main__':
    base = "https://en.wikipedia.org"
    link = "/wiki/Jarvis_Island/People"

    # global queue
    q = queue.Queue()

    rab = Rabbit()

    table = {}

    # seen links overall since emptying the dict to save memory
    links = []
    processed = []
    index = 0

    storage_file = "new_store"

    # checks for storage file and loads storage file
    try:
        with shelve.open(storage_file) as file:
            print(list(file.keys()))
            links = file['processed']
            index = file['index']
            file.close()
    except KeyError:
        print("New file created")

    # includes "see also" part
    xpath = '//div[@id="mw-content-text"]//p//a'

    # clean up link
    if link.count("/") > 2:
        link = "/".join(link.split("/")[:3])

    # create threads and establish thread "signal" variable
    not_done = True
    for _ in range(10):
        t = threading.Thread(target=worker)
        t.start()

    process_wiki(link, 2)

    # LOOP FOR CHECKING WHEN IT IS DONE AND ALSO WRITING to pickle file
    while True:
        index += 1
        time.sleep(5)
        # check if table has not changed since last cycle
        if not table:
            not_done = False
            break
        # writes to storage file
        with shelve.open(storage_file) as file:
            file['processed'] = links
            file[str(index)] = table
            file['index'] = index
            file.close()

        rab.send_dict(table)

        processed = []
        table = {}

    with shelve.open(storage_file) as file:
        for x in list(file.keys()):
            try:
                int(x)
            except ValueError:
                continue

        file.close()
