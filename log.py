# coding: utf-8
import os
import logging.handlers
import datetime


def make_dir(make_dir_path):
    path = make_dir_path.strip()
    if not os.path.exists(path):
        os.makedirs(path)
    return path


log_file_folder = 'logs'
make_dir(log_file_folder)
logger = logging.getLogger('udo')
logger.setLevel(logging.INFO)

s_handler = logging.StreamHandler()
s_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s")
s_handler.setFormatter(formatter)

rf_handler = logging.handlers.TimedRotatingFileHandler('logs/svc-codex-udo.log', when='MIDNIGHT', interval=1, backupCount=7, atTime=datetime.time(0, 0, 0, 0))
rf_handler.setFormatter(formatter)

logger.addHandler(rf_handler)
logger.addHandler(s_handler)

