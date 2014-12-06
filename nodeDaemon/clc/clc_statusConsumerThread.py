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
        self.mc = memcache.Client(['127.0.0.1:11211'], debug=0)

    def save2Mem(self, key, msg):
        try:
            self.mc.set(key, msg)
            logger.error("add to memcaceh: %s" % msg)
        except Exception as e:
            logger.errro(e.message)

    def forwardMessage2Memcache(self, message):
        json_msg = json.loads(message)
        if json_msg['type'] == 'taskstatus':
            logger.error("get task status msg: %s" % message)
            key = str(json_msg['tid'])
        elif json_msg['type'] == 'nodestatus':
            logger.error("get node status msg: %s" % message)
            key = json_msg['nid']

        self.save2Mem(key, json_msg)


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
