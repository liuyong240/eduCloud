from luhyaapi.run4everProcess import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
import time, json

logger = getwalrusdaemonlogger()

class walrus_statusPublisherThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)

    def statusMessageHandle(self, ch, method, properties, body):
        pass

    def run4ever(self):
        connection = getConnection("localhost")
        channel = connection.channel()
        channel.queue_declare(queue='walrus_status_queue')
        channel.basic_consume(self.statusMessageHandle,
                              queue='walrus_status_queue',
                              no_ack=True)
        channel.start_consuming()
