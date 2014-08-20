from luhyaapi.run4everProcess import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.rabbitmqWrapper import *
import pika, json, time

logger = getncdaemonlogger()

download_rpc = RpcClient(logger, '192.168.56.101', 'cc_status_queue')
response = download_rpc.call(cmd="image/download", paras="xp:imgid-abcd:insid-1234")
print response

