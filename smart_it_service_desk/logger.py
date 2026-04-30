import logging
import os
from datetime import datetime
from .utils import append_text

BASE_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(BASE_DIR, 'data', 'logs.txt')


def configure_logger():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logger = logging.getLogger('smart_it_service_desk')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


logger = configure_logger()


def log_event(level, message):
    if level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    elif level == 'critical':
        logger.critical(message)
    else:
        logger.debug(message)
    append_text(LOG_FILE, f"{datetime.now().isoformat()} {level.upper()} {message}")


def action_logger(func):
    def wrapper(*args, **kwargs):
        log_event('info', f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        log_event('info', f"Completed {func.__name__}")
        return result
    return wrapper
