from luhyaapi.run4everProcess import *
from luhyaapi.rabbitmqWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
import time, json
import memcache

logger = getclcdaemonlogger()

class clc_statusConsumerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)
        self.mc = mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    def forwardMessage2Memcache(self, message):
        json_msg = json.loads(message)
        tid = json_msg['tid']
        self.mc.set(tid, json_msg)
        logger.error("add to memcaceh: %s" % message)

    def statusMessageHandle(self, ch, method, properties, body):
        self.forwardMessage2Memcache(body)

    def run4ever(self):
        connection = getConnection("localhost")
        channel = connection.channel()
        channel.queue_declare(queue='clc_status_queue')
        channel.basic_consume(self.statusMessageHandle,
                              queue='clc_status_queue',
                              no_ack=True)
        channel.start_consuming()
