# -*- coding: utf-8 -*-
from conf.data_env_config import *
from loguru import logger


class LoggerModule():
    def __init__(self, log_file=log_file, format="{time} {level} {message}"):
        self.log_file = log_file
        self.format = format
        logger.add(self.log_file)
        print(logger)

    def logging(self, message, level="INFO"):
        if level.upper() == "INFO":
            return logger.info(message)
        elif level.upper() == "DEBUG":
            return logger.debug(message)
        elif level.upper() == "WARNING":
            return logger.warning(message)
        elif level.upper() == "ERROR":
            return logger.error(message)
        elif level.upper() == "SUCCESS":
            return logger.success(message)
        elif level.upper() == "CRITICAL":
            return logger.critical(message)
        else:
            return logger.info(message)


if __name__ == '__main__':
    LOG = LoggerModule()
    msg = ["info", "debug", "warning", "error", "success", "critical"]

    for i in msg:
        LOG.logging(f"{i} msg", i)
