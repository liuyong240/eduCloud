from luhyaapi.rabbitmqWrapper import *
from luhyaapi.hostTools import *
from luhyaapi.educloudLog import *
from luhyaapi.settings import *
import time, requests

logger = getccdaemonlogger()

class cc_statusConsumer():
    def __init__(self, ):
        logger.error("cc_status_consumer start running")
        self.clcip = getclcipbyconf()

    def forwardTaskStatus2CLC(self, message):
        simple_send(logger, self.clcip, 'clc_status_queue', message)

    def statusMessageHandle(self, ch, method, properties, body):
        self.forwardTaskStatus2CLC(body)

    def run(self):
        connection = getConnection("localhost")
        channel = connection.channel()
        channel.queue_declare(queue='cc_status_queue')
        channel.basic_consume(self.statusMessageHandle,
                              queue='cc_status_queue',
                              no_ack=True)
        channel.start_consuming()

def perform_mount():
    logger.error("Enter perform_mount() ... ...")
    # mount clc's /storage/space/{software, pub-data} to local
    if amIwalrus():
        logger.error("I am cc and walrus, no mount any more.")
        return

    clcip = getclcipbyconf()
    cmd_line = 'id -u luhya'
    luhya_id = commands.getoutput(cmd_line)
    base_cmd = 'echo luhya | sshfs -o uid=%s,gid=%s,cache=yes,allow_other,password_stdin,reconnect luhya@%s:/storage/space /storage/space'

    if not os.path.ismount('/storage/space'):
        cmd1 = base_cmd % (luhya_id, luhya_id, clcip)
        logger.error(cmd1)
        os.system(cmd1)
    else:
        logger.error("/storage/space is already mounted ... ...")


def registerMyselfasCC():
    logger.error("Enter registerMyselfasCC() ... ...")

    clcip = getclcipbyconf(mydebug=DAEMON_DEBUG)
    ccname = getccnamebyconf()

    hostname, hostcpus, hostmem, hostdisk = getHostAttr()
    netlist = getHostNetInfo()
    if DAEMON_DEBUG == True:
        url = 'http://%s:8000/clc/api/1.0/register/server' % clcip
    else:
        url = 'http://%s/clc/api/1.0/register/server' % clcip
    payload = {
        'role': 'cc',
        'name': hostname,
        'cores': hostcpus,
        'memory': hostmem,
        'disk': hostdisk,
        'exip': netlist['exip'],
        'ip0': netlist['ip0'],
        'ip1': netlist['ip1'],
        'ip2': netlist['ip2'],
        'ip3': netlist['ip3'],
        'mac0': netlist['mac0'],
        'mac1': netlist['mac1'],
        'mac2': netlist['mac2'],
        'mac3': netlist['mac3'],
        'ccname': ccname,
        'hypervisor': getHypervisor(),
    }
    logger.error("send request %s " % url)
    r = requests.post(url, data=payload)
    return r.status_code

def main():
    # read /storage/config/cc.conf to register itself to cc
    registerMyselfasCC()
    perform_mount()

    consumer = cc_statusConsumer()
    consumer.run()

if __name__ == '__main__':
    main()
