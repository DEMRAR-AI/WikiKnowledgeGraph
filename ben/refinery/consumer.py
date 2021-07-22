import datetime
import http.server as http
import json
import socketserver
import threading
import os
import psutil
import time
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pika
from neomodel import StructuredNode, StringProperty, Relationship, config


class Basic(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    to = Relationship("Basic", "related_to")
    link = StringProperty(required=False)


class DiagnosticRequestHandler(http.SimpleHTTPRequestHandler):
    def do_GET(self):
        global killed

        self.send_response(200)

        self.send_header("Content-type", "text/html")
        self.end_headers()

        # get query components, if none then just get all info
        q_comps = parse_qs(urlparse(self.path).query)
        if 'cmd' in q_comps:
            cmd = q_comps['cmd'][0]
            if 'kill' in cmd:
                log("Stopped consumer")
                killed = True
        html = "Info:"

        self.wfile.write(bytes(html, 'utf8'))

        return


def log(msg):
    with open("log.txt", "a+") as file:
        file.write("\n[" + str(datetime.datetime.now()).split(".")[0] + "]: " + msg)
        file.close()


def diagnostic():
    handler_obj = DiagnosticRequestHandler

    port = 8000
    dg_server = socketserver.TCPServer(("", port), handler_obj)

    dg_server.serve_forever()


def MQ():
    host = '45.79.94.203'
    creds = pika.PlainCredentials('main', 'main13')
    con = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=creds))
    channel = con.channel()

    channel.queue_declare(queue='main_q', passive=True)

    channel.basic_consume(queue='main_q', auto_ack=True, on_message_callback=callback)

    log("Started consumer")

    channel.start_consuming()


# where the magic happens
def callback(ch, method, properties, body):
    unjsoned = json.loads(body)

    for key in unjsoned:
        search = Basic.nodes.get_or_none(link=key)
        if not search:
            search = Basic(link=key)
        this_node = search
        for rel in unjsoned[key]:
            # search for node in graph and if there is none then create one and connect after either
            search = Basic.nodes.get_or_none(link=rel)
            if search:
                this_node.to.connect(search)
            else:
                # CAN CHANGE NODE SETUP AND PROCESSING
                new_node = Basic(link=rel)
                this_node.to.connect(new_node)


if __name__ == '__main__':
    killed = False
    try:
        user = "neo4j"
        password = "neo123"

        server = "bolt://{}:{}@localhost:7474".format(user, password)
        config.DATABASE_URL = server

        t1 = threading.Thread(target=diagnostic)
        t1.start()

        t2 = threading.Thread(target=MQ)
        t2.start()

        while not killed:
            time.sleep(.6)

    finally:
        pid = os.getpid()

        ts = psutil.Process(pid)
        ts.terminate()
