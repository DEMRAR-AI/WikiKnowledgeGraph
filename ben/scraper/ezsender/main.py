import pika
import json


class ConError(Exception):
    def __init__(self, msg="Not connected to a RabbitMQ server!"):
        super(ConError, self).__init__(msg)


class Rabbit(object):
    def __init__(self):
        self.host = None
        self.con = None
        self.channel = None

    def connect(self, host='45.79.94.203'):
        self.host = host
        creds = pika.PlainCredentials('main', 'main13')
        self.con = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=creds))
        self.channel = self.con.channel()
        self.channel.queue_declare(queue='main_q', passive=True)

    def send_dict(self, d):
        if type(d) != dict:
            raise TypeError("Only dictionaries allowed!")
        if not self.con:
            raise ConError()

        jsoned = json.dumps(d)

        self.channel.basic_publish(exchange='', routing_key='main_q', body=jsoned)

    def close(self):
        self.con.close()
