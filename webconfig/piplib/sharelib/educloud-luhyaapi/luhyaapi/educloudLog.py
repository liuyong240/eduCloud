import logging
import logging.handlers
from settings import *


MAX_LOGFILE_BYTE = 10 * 1024 * 1024
MAX_LOG_COUNT = 10


def init_log(logfile, loggername):
    logger = logging.getLogger(loggername)
    ch = logging.handlers.RotatingFileHandler(logfile, maxBytes=MAX_LOGFILE_BYTE, backupCount=MAX_LOG_COUNT)
    formatter = logging.Formatter('<%(asctime)s> <%(levelname)s> <%(module)s:%(lineno)d>\t%(message)s', datefmt='%F %T')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.ERROR)
    return logger


DEBUG_LOG_FILE = '/var/log/educloud/luhya-debug.log'
luhya_debug_logger = init_log(DEBUG_LOG_FILE, 'luhya_debug')

CLC_DAEMON_LOG_FILE = '/var/log/educloud/clc_daemon.log'
clc_daemon_logger = init_log(CLC_DAEMON_LOG_FILE, 'clc_daemon')

WALRUS_DAEMON_LOG_FILE = '/var/log/educloud/walrus_daemon.log'
walrus_daemon_logger = init_log(WALRUS_DAEMON_LOG_FILE, 'walrus_daemon')

CC_DAEMON_LOG_FILE = '/var/log/educloud/cc_daemon.log'
cc_daemon_logger = init_log(CC_DAEMON_LOG_FILE, 'cc_daemon')

NC_DAEMON_LOG_FILE = '/var/log/educloud/nc_daemon.log'
nc_daemon_logger = init_log(NC_DAEMON_LOG_FILE, 'nc_daemon')


def getclcdaemonlogger():
    if DAEMON_DEBUG:
        return luhya_debug_logger
    else:
        return clc_daemon_logger


def getwalrusdaemonlogger():
    if DAEMON_DEBUG:
        return luhya_debug_logger
    else:
        return walrus_daemon_logger


def getccdaemonlogger():
    if DAEMON_DEBUG:
        return luhya_debug_logger
    else:
        return cc_daemon_logger


def getncdaemonlogger():
    if DAEMON_DEBUG:
        return luhya_debug_logger
    else:
        return nc_daemon_logger


CLC_LOG_FILE = '/var/log/educloud/clc.log'
clc_logger = init_log(CLC_LOG_FILE, 'clc')

WALRUS_LOG_FILE = '/var/log/educloud/walrus.log'
walrus_logger = init_log(WALRUS_LOG_FILE, 'walrus')

CC_LOG_FILE = '/var/log/educloud/cc.log'
cc_logger = init_log(CC_LOG_FILE, 'cc')

NC_LOG_FILE = '/var/log/educloud/nc.log'
nc_logger = init_log(NC_LOG_FILE, 'nc')


def getclclogger():
    if DAEMON_DEBUG:
        return luhya_debug_logger
    else:
        return clc_logger


def getwalruslogger():
    if DAEMON_DEBUG:
        return luhya_debug_logger
    else:
        return walrus_logger


def getcclogger():
    if DAEMON_DEBUG:
        return luhya_debug_logger
    else:
        return cc_logger


def getnclogger():
    if DAEMON_DEBUG:
        return luhya_debug_logger
    else:
        return nc_logger
