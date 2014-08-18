import pika
import time
import threading

class worker(threading.Thread):
    def __init__(self, message):
        threading.Thread.__init__(self)
        self.msg = message

    def run(self):
        print ' process message as %s ' % self.msg
        time.sleep(10)
        print ' work is done '


connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='test',
                         type='direct')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='test',
	   queue=queue_name,
	   routing_key="quue1")

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
    print " [x] %r:%r" % (method.routing_key, body,)
    wt = worker(body)
    wt.start()
    

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
