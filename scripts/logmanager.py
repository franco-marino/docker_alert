import logging
from os import getenv
from logging.handlers import RotatingFileHandler

def create_logger():
    logger = logging.getLogger("docker_alert")

    logger.setLevel(getenv("LOG_LEVEL"))

    path         = getenv("LOG_PATH")
    max_bytes    = int(getenv("LOG_ROTATE_MAX_BYTES"))
    backup_count = int(getenv("LOG_ROTATE_BACKUP_COUNT"))

    handler = RotatingFileHandler(
        path, maxBytes=max_bytes, backupCount=backup_count
    )

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: \t%(message)s", datefmt="%Y/%m/%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)


