# -*- coding: utf-8 -*-
# @Time    : 2020/11/17 11:37
# @Author  : weidengyi


from loguru import logger
import os
from conf.PATH_CONF import LOG_PATH
if os.path.exists(LOG_PATH) and os.path.isdir(LOG_PATH):
    pass
else:
    os.mkdir(LOG_PATH)
logger.add("{0}/log.log".format(LOG_PATH))