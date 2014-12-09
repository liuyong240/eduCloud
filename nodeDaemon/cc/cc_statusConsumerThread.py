from luhyaapi.run4everProcess import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
import time

logger = getccdaemonlogger()

class cc_statusConsumerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)
        self.clcip = getclcipbyconf()

    def forwardTaskStatus2CLC(self, message):
        simple_send(logger, self.clcip, 'clc_status_queue', message)

    def statusMessageHandle(self, ch, method, properties, body):
        self.forwardTaskStatus2CLC(body)

    def run4ever(self):
        connection = getConnection("localhost")
        channel = connection.channel()
        channel.queue_declare(queue='cc_status_queue')
        channel.basic_consume(self.statusMessageHandle,
                              queue='cc_status_queue',
                              no_ack=True)
        channel.start_consuming()
