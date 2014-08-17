from luhyaapi.run4everProcess import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
import pika, json, time

logger = getncdaemonlogger()

def nc_imagebuild_handle(srcid, destid):
    time.sleep(100)

def nc_imagemodify_handle(srcid, destid):
    time.sleep(100)

nc_cmd_handlers = {
    'imagebuild'    : nc_imagebuild_handle,
    'imagemodify'   : nc_imagemodify_handle,
}


class nc_cmdConsumerThread(run4everThread):
    def __init__(self, bucket, logger):
        run4everThread.__init__(self, bucket)



    def cmdHandle(self, ch, method, properties, body):
        logger.error(" [x] %r:%r" % (method.routing_key, body))
        message = json.loads(body)
        nc_cmd_handlers[message['op']](message['paras'])

    def run4ever(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange='cc_cmd',
                                 type='direct')

        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        ip0 = getHostNetInfo()['ip0']

        channel.queue_bind(exchange='cc_cmd',
                           queue=queue_name,
                           routing_key=ip0)

        channel.basic_consume(self.cmdHandle,
                              queue=queue_name,
                              no_ack=True)

        channel.start_consuming()
