from luhyaapi.run4everProcess import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
import time

logger = getclcdaemonlogger()

def callback(ch, method, properties, body):
    # save body into memcache
    pass

class clc_statusConsumerThread(run4everThread):
    def __init__(self, bucket, logger):
        run4everThread.__init__(self, bucket, logger)

    def run4ever(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='clc_status_queue')
        channel.basic_consume(callback,
                              queue='clc_status_queue',
                              no_ack=True)
        channel.start_consuming()
