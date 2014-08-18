import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
message = "imagebuild"
channel.exchange_declare(exchange="test",
			 type='direct')
channel.basic_publish(exchange="test",
		  routing_key="quue1",
		  body=message)
connection.close()


