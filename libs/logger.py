# -*- coding: utf-8 -*-
# @Time    : 2021/5/18 16:01
# @Author  : weidengyi

# import logging
# import logging.handlers
# import os
# import time


from loguru import logger
import os
from conf.PATH_CONF import LOG_PATH
if os.path.exists(LOG_PATH) and os.path.isdir(LOG_PATH):
    pass
else:
    os.mkdir(LOG_PATH)
logger.add(LOG_PATH)

if __name__ == '__main__':
    logger.info()
    # main()



# def singleton(cls):
#     instances = {}
#     def _singleton(*args, **kwargs):
#         if cls not in instances:
#             instances[cls] = cls(*args, **kwargs)
#         return instances[cls]
#
#     return _singleton
#
#
# @singleton
# class LogWrapper(object):
#     def __init__(self):
#         self.logger = logging.getLogger("")
#
#         # 设置输出的等级
#         LEVELS = {'NOSET': logging.NOTSET,
#                   'DEBUG': logging.DEBUG,
#                   'INFO': logging.INFO,
#                   'WARNING': logging.WARNING,
#                   'ERROR': logging.ERROR,
#                   'CRITICAL': logging.CRITICAL}
#
#         logging.getLogger("paramiko").setLevel(logging.WARNING)
#         # 创建文件目录
#         if os.path.exists(LOG_PATH) and os.path.isdir(LOG_PATH):
#             pass
#         else:
#             os.mkdir(LOG_PATH)
#
#         # 修改log保存位置
#         timestamp = time.strftime("%Y-%m-%d", time.localtime())
#         logfilename = '%s.txt' % timestamp
#         logfilepath = os.path.join(LOG_PATH, logfilename)
#         rotatingFileHandler = logging.handlers.RotatingFileHandler(filename=logfilepath,
#                                                                    maxBytes=1024 * 1024 * 50,
#                                                                    backupCount=5)
#
#         # 设置输出格式
#         formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')
#         rotatingFileHandler.setFormatter(formatter)
#
#         # 控制台句柄
#         console = logging.StreamHandler()
#         console.setLevel(logging.NOTSET)
#         console.setFormatter(formatter)
#
#         # 添加内容到日志句柄中
#         self.logger.addHandler(rotatingFileHandler)
#         self.logger.addHandler(console)
#         self.logger.setLevel(logging.NOTSET)
#
#     def info(self, message):
#         self.logger.info(message)
#
#     def debug(self, message):
#         self.logger.debug(message)
#
#     def warning(self, message):
#         self.logger.warning(message)
#
#     def error(self, message):
#         self.logger.error(message)
#
#
# def main():
#     log_wrapper = LogWrapper()
#     log_wrapper.info("this is info")
#     log_wrapper.debug("this is debug")
#     log_wrapper.error("this is error")
#     log_wrapper.warning("this is warning")


if __name__ == '__main__':
    pass
    # main()

