from py2neo import Graph, Node, Relationship
from Scraper import Scraper
import os
import shelve
import spacy

class Refinery(object):
    def __init__(self, uri, user, password):
        self.graph = Graph(uri=uri, user=user, password=password)

    def push_to_cache(self, file_path, data):
        cache = shelve.open(file_path)
        for key in data:
            branches = list(data[key])
            cache[key] = branches
        return True

    def push_to_db(self, data, clear=False):
        if data == None or len(data) == 0:
            print('no data to push')
            return False
        nodes = dict()
        nlp = spacy.load('en_core_web_lg')
        if clear:
            self.graph.delete_all()
        for key in data:
            if key not in nodes.keys():
                key_doc = nlp(Scraper.clean_str(key))
                if len(key_doc.ents) > 0:
                    key_label = key_doc.ents[0].label_
                else:
                    key_label = 'PAGE'
                nodes[key] = Node(key_label, name=key)
                self.graph.create(nodes[key])
            branch_nodes = data[key]
            for bn in branch_nodes:
                if bn not in nodes.keys():
                    bn_doc = nlp(Scraper.clean_str(bn))
                    if len(bn_doc.ents) > 0:
                        bn_label = bn_doc.ents[0].label_
                    else:
                        bn_label = 'PAGE'
                    nodes[bn] = Node(bn_label, name=bn)
                    self.graph.create(nodes[bn])
                self.graph.create(Relationship(nodes[key], 'related to', nodes[bn]))
        return True
