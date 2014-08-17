import pika

def routing_send(logger, serverIP, exchangeName,  message, routingKey):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=serverIP))
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

def routing_recieve():
    pass
