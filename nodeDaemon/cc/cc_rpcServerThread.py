from luhyaapi.run4everProcess import *
from luhyaapi.educloudLog import *
from luhyaapi.clcAPIWrapper import *
from luhyaapi.hostTools import *

import time, pika, json

logger = getccdaemonlogger()

class downloadWorkerThread(threading.Thread):
    def __init__(self, ch, method, props,  dstip, tid):
        threading.Thread.__init__(self)
        self.ch = ch
        self.props = props
        self.method = method

        self.dstip    = dstip
        self.tid      = tid
        retval = tid.split(':')
        self.srcimgid = retval[0]

    def run(self):
        index = 0
        while True:
            time.sleep(1)
            payload = {
                'type'  : 'taskstatus',
                'phase' : "downloading",
                'progress'  : index,
                'tid'   :  self.tid
            }

            self.ch.basic_publish(exchange='',
                     routing_key=self.props.reply_to,
                     properties=pika.BasicProperties(correlation_id = self.props.correlation_id),
                                                     body=json.dumps(payload))
            self.ch.basic_ack(delivery_tag = self.method.delivery_tag)
            index = index + 1
            if index > 100:
                break


def cc_rpc_handle_imagedownload(ch, method, props, tid):
    clcip = getclcipbyconf()
    walrusIP = getWalrusInfo(clcip)
    worker = downloadWorkerThread(ch, method, props, walrusIP, tid)
    worker.start()
    return worker

cc_rpc_handlers = {
    'image/download'    : cc_rpc_handle_imagedownload,
}

def on_request(ch, method, props, body):
    message = json.loads(body)
    if cc_rpc_handlers[message['op']] != None:
        cc_rpc_handlers[message['op']](ch, method, props, message['paras'])
    else:
        logger.error("unknow cmd : %s", message['op'])


class cc_rpcServerThread(run4everThread):
    def __init__(self, bucket):
        run4everThread.__init__(self, bucket)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')
        self.channel.basic_qos(prefetch_count=1)

    def run4ever(self):
        self.channel.basic_consume(on_request, queue='rpc_queue')
        self.channel.start_consuming()




