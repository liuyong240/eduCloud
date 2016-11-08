import zmq

from luhyaapi.educloudLog import *
logger = getclclogger()

CLC_CMD_QUEUE_PORT = 9997
CC_CMD_QUEUE_PORT  = 9998
NC_CMD_QUEUE_PORT  = 9999

def zmq_send(ip, msg, port):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://%s:%s" % (ip,port))

    socket.send(msg)
    message = socket.recv()
    logger.error("zmq_send result = %s" % message)

def zmq_recv():
    pass