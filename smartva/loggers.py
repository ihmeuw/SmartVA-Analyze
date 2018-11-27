import logging
from logging.handlers import MemoryHandler

logger = logging.getLogger()

status_logger = logging.getLogger('status')
status_logger.setLevel(logging.INFO)

warning_logger = logging.getLogger('warning')
warning_logger.setLevel(logging.INFO)

report_logger = logging.getLogger('report')
report_logger.setLevel(logging.INFO)
report_logger.addHandler(
    MemoryHandler(capacity=float('inf'), flushLevel=logging.CRITICAL))

REPORT_LOGGERS_NAMES = (
    'sids',
    'refused',
    'valid_consent',
    'valid_age',
    'prediction',
)
for name in REPORT_LOGGERS_NAMES:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = MemoryHandler(capacity=float('inf'), flushLevel=logging.CRITICAL)
    logger.addHandler(handler)
