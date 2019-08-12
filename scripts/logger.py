import logging
import time
import os
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, path=None, external=False):
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: \t%(message)s", datefmt="%Y/%m/%d %H:%M:%S"
        )
        self.logger = logging.getLogger("logger")
        if external:
            handler = logging.FileHandler(path)
        else:
            path = os.getenv("LOG_PATH")
            max_bytes = int(os.getenv("LOG_ROTATE_MAX_BYTES"))
            backup_count = int(os.getenv("LOG_ROTATE_BACKUP_COUNT"))
            handler = RotatingFileHandler(
                path, maxBytes=max_bytes, backupCount=backup_count
            )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, type, log):
        if type == "error":
            self.logger.setLevel(logging.ERROR)
            self.logger.error(log)
        elif type == "critical":
            self.logger.setLevel(logging.CRITICAL)
            self.logger.critical(log)
        else:
            self.logger.setLevel(logging.INFO)
            self.logger.info(log)

