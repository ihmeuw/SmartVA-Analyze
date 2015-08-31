import logging

logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

status_logger = logging.getLogger('status')
status_logger.setLevel(logging.INFO)
