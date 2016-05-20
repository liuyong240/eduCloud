import time
from luhyaapi.educloudLog import *

logger = getccdaemonlogger()

class cc_cmdConsumer():
    def __init__(self, ):
        logger.error("cc_cmd_consumer start running")

    def run(self):
        while True:
            time.sleep(100)

def main():
    consumer = cc_cmdConsumer()
    consumer.run()

if __name__ == '__main__':
    main()