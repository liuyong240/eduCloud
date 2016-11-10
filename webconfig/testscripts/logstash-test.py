import logging
logging.basicConfig()
from structlog import get_logger, configure
from structlog.stdlib import LoggerFactory
configure(logger_factory=LoggerFactory())
log = get_logger()
log.error('it works!', difficulty='easy')
