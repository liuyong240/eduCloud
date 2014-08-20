from luhyaapi.educloudLog import *
from luhyaapi.rabbitmqWrapper import *

logger = getclcdaemonlogger()

ncip = "192.168.56.101"
message = {}
message['type'] = "cmd"
message['op']   = 'image/create'
message['paras']= "xp:imgid-abcd:insid-1234"
message = json.dumps(message)
routing_send(logger, 'localhost', 'nc_cmd', message, ncip)
