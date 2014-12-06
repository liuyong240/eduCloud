import pika, uuid, json, time

def getConnection(serverIP):
    credentials = pika.PlainCredentials('luhya', 'luhya')
    cpara = pika.ConnectionParameters(host=serverIP, credentials=credentials)
    connection = pika.BlockingConnection(cpara)
    return connection

def simple_send(logger, serverIP, queue_name, message):
    connection = getConnection(serverIP)

    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=message)
    connection.close()
    logger.error("luhya: send message %s to %s in %s" % (message, queue_name, serverIP))

def routing_send(logger, serverIP, exchangeName,  message, routingKey):
    connection = getConnection(serverIP)

    channel = connection.channel()
    channel.exchange_declare(exchange=exchangeName,
                             type='direct')
    channel.basic_publish(exchange=exchangeName,
                          routing_key=routingKey,
                          body=message)
    connection.close()
    logger.error("Send a message to command queue")
    logger.error("---- exchange Name: %s" % exchangeName)
    logger.error("---- routing Key  : %s" % routingKey)
    logger.error("---- message      : %s" % message)

# main tasks are
# 1. ask serverIP to do a long time job
# 2. get the job status and send to serverIP's server_status_queue
# 3. until job finished, return OK
class RpcClient(object):
    def __init__(self, logger, serverIP):
        self.logger = logger
        self.serverIP = serverIP

        self.connection = getConnection(serverIP)

        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, cmd, paras, timeout=0):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        payload = {
            'type'  :   'cmd',
            'op'    :   cmd,
            'paras' :   paras
        }
        payload = json.dumps(payload)
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=payload)

        while self.response is None:
            self.connection.process_data_events()

        # send status to CC's status queue
        return self.response
