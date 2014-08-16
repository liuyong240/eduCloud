#!/usr/bin/python -u

__version__ = '1.0.0'

import sys
import os
import logging
import logging.handlers
import time
import datetime

MAX_LOGFILE_BYTE=10*1024*1024
LOG_FILE='/var/log/educlooud/cc_daemon.log'
MAX_LOG_COUNT=10

def init_log():
  logger = logging.getLogger('')
  ch = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOGFILE_BYTE,backupCount=MAX_LOG_COUNT)
  formatter = logging.Formatter('<%(asctime)s> <%(levelname)s> <%(module)s:%(lineno)d>\t%(message)s' , datefmt='%F %T')
  ch.setFormatter(formatter)
  logger.addHandler(ch)
  logger.setLevel(logging.ERROR)
  return logger


logger = init_log()

'''

start a few worker thread
if there worker thread dies, restart them
list of daemon and worker thread

1. a status_queue consumer deamon, after process based on message type, forwarding to CLC's status_queue

2. a status report daemon, periodically report CC status to CLC's status_queue

3. a cmd_queue comsumer daemon for handler RPC like
3.1  download image from walrus
3.2  upload image to walrus

'''
def main ():



  while True:
          time.sleep(100000)


if __name__ == '__main__':
  main ()