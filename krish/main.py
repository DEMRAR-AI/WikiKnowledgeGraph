from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from py2neo import Graph, Node, Relationship
import spacy
import os
import time

ROOT = '/wiki/television'
DRIVER_PATH = 'C:\Program Files (x86)\chromedriver.exe'
PREFIX = 'https://www.wikipedia.com'
CASES = ['Special', 'Help', 'File', 'cite', 'wikipedia', 'Wikipedia']

nodes = dict()
driver = webdriver.Chrome(DRIVER_PATH)

def _contains(str):
    for case in CASES:
        if case in str:
            return True
    return False

def _get_branch_nodes(pg):
    main_p = None
    a_tags = list()
    a_tag_dict = dict()
    driver.get(PREFIX + pg)
    ps = driver.find_elements_by_tag_name('p')
    for p in ps:
        try:
            p.find_element_by_tag_name('b')
            if len(p.find_elements_by_tag_name('a')) > 0:
                main_p = p
                break
            else:
                continue
        except NoSuchElementException:
            continue
    if main_p == None:
        print('invalid page format')
        return None
    # print(main_p.text)
    a_tags = main_p.find_elements_by_tag_name('a')
    for a_tag in a_tags:
        href = a_tag.get_attribute('href')
        href = href[href.find('g/') + 1:]
        if not _contains(href):
            a_tag_dict[a_tag.text] = href
    return a_tag_dict.values()

def process(depth=3, root=ROOT):
    if root == None or len(root) == 0:
        return False
    if depth == 0:
        return True
    data = _get_branch_nodes(root)
    nodes[root] = data
    for dt in data:
        process(depth-1, dt)


def clean_str(str):
    if '/wiki/' in str:
        str = str[str.find('i/')+2:]
    str = str.replace('_', ' ')
    return str

def push_data(data, clear=False):
    if data == None or len(data) == 0:
        print('no data to push')
        return False
    nodes = dict()
    graph = Graph(password='abc123')
    nlp = spacy.load('en_core_web_lg')
    if clear:
        graph.delete_all()
    for key in data:
        if key not in nodes.keys():
            key_doc = nlp(clean_str(key))
            if len(key_doc.ents) > 0:
                key_label = key_doc.ents[0].label_
            else:
                key_label = 'PAGE'
            nodes[key] = Node(key_label, name=key)
            graph.create(nodes[key])
        branch_nodes = data[key]
        for bn in branch_nodes:
            if bn not in nodes.keys():
                bn_doc = nlp(clean_str(bn))
                if len(bn_doc.ents) > 0:
                    bn_label = bn_doc.ents[0].label_
                else:
                    bn_label = 'PAGE'
                nodes[bn] = Node(bn_label, name=bn)
                graph.create(nodes[bn])
            graph.create(Relationship(nodes[key], 'related to', nodes[bn]))
    return True

if __name__ == '__main__':
    process(depth=3, root=ROOT)
    push_data(nodes)
    driver.close()