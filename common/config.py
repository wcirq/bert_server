# -*- coding: utf-8 -*- 
# @Time 2020/5/12 12:22
# @Author wcy

import logging.handlers
import os
from common.path_control import LOG_DIR

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
if not os.path.exists(os.path.dirname(LOG_DIR)):
    os.makedirs(os.path.dirname(LOG_DIR))
handler = logging.handlers.TimedRotatingFileHandler(LOG_DIR, when='H', interval=6, backupCount=40)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(filename)s][%(funcName)s][line:%(lineno)d][%(levelname)s] %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console)
