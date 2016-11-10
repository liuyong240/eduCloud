import logging
import logging.handlers
from settings import *


MAX_LOGFILE_BYTE = 10 * 1024 * 1024
MAX_LOG_COUNT = 10


def set_log_level(level, loggername='luhya'):
    logger = logging.getLogger(loggername)
    if level == 'error':
        logger.setLevel(logging.ERROR)
    elif level == 'warning':
        logger.setLevel(logging.WARNING)
    elif level == 'info':
        logger.setLevel(logging.INFO)


def init_log(logfile, loggername='luhya'):
    logger = logging.getLogger(loggername)
    ch = logging.handlers.RotatingFileHandler(logfile, maxBytes=MAX_LOGFILE_BYTE, backupCount=MAX_LOG_COUNT)
    formatter = logging.Formatter('<%(asctime)s> <%(levelname)s> <%(module)s:%(lineno)d>\t%(message)s', datefmt='%F %T')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.ERROR)
    return logger


DEBUG_LOG_FILE = '/var/log/educloud/luhya-debug.log'
luhya_debug_logger = init_log(DEBUG_LOG_FILE)

NC_DEBUG_LOG_FILE = '/var/log/educloud/nc.log'
nc_debug_logger = init_log(NC_DEBUG_LOG_FILE, 'node')

def getclcdaemonlogger():
    return luhya_debug_logger

def getwalrusdaemonlogger():
    return luhya_debug_logger

def getccdaemonlogger():
    return luhya_debug_logger

def getncdaemonlogger():
    return nc_debug_logger

def getclclogger():
    return luhya_debug_logger

def getwalruslogger():
    return luhya_debug_logger

def getcclogger():
    return luhya_debug_logger

def getnclogger():
    return luhya_debug_logger

def geteducloudlogger():
    return luhya_debug_logger
