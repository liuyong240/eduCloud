import logging
import logging.handlers

MAX_LOGFILE_BYTE = 10 * 1024 * 1024
MAX_LOG_COUNT = 10

def init_log(logfile):
    logger = logging.getLogger('')
    ch = logging.handlers.RotatingFileHandler(logfile, maxBytes=MAX_LOGFILE_BYTE, backupCount=MAX_LOG_COUNT)
    formatter = logging.Formatter('<%(asctime)s> <%(levelname)s> <%(module)s:%(lineno)d>\t%(message)s', datefmt='%F %T')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.ERROR)
    return logger

CLC_DAEMON_LOG_FILE = '/var/log/educloud/clc_daemon.log'
clc_daemon_logger = init_log(CLC_DAEMON_LOG_FILE)

WALRUS_DAEMON_LOG_FILE = '/var/log/educloud/walrus_daemon.log'
walrus_daemon_logger = init_log(WALRUS_DAEMON_LOG_FILE)

CC_DAEMON_LOG_FILE = '/var/log/educloud/cc_daemon.log'
cc_daemon_logger = init_log(CC_DAEMON_LOG_FILE)

NC_DAEMON_LOG_FILE = '/var/log/educloud/nc_daemon.log'
nc_daemon_logger = init_log(NC_DAEMON_LOG_FILE)

def getclcdaemonlogger():
    return clc_daemon_logger

def getwalrusdaemonlogger():
    return walrus_daemon_logger

def getccdaemonlogger():
    return cc_daemon_logger

def getncdaemonlogger():
    return nc_daemon_logger

CLC_LOG_FILE = '/var/log/educloud/clc.log'
clc_logger = init_log(CLC_LOG_FILE)

WALRUS_LOG_FILE = '/var/log/educloud/walrus.log'
walrus_logger = init_log(WALRUS_LOG_FILE)

CC_LOG_FILE = '/var/log/educloud/cc.log'
cc_logger = init_log(CC_LOG_FILE)

NC_LOG_FILE = '/var/log/educloud/nc.log'
nc_logger = init_log(NC_LOG_FILE)

def getclclogger():
    return clc_logger

def getwalruslogger():
    return walrus_logger

def getcclogger():
    return cc_logger

def getnclogger():
    return nc_logger