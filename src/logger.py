import logging
from pathlib import PurePath
from logging.handlers import RotatingFileHandler
from src.config import config

class Logger():
    @property
    def logger(self):
        name = '.'.join([
            config.get('name').split('.')[0]
        ])
        lg = logging.getLogger(name)
        lg.setLevel(10)
        formatter = logging.Formatter(
            '%(name)s %(asctime)s %(levelname)s [%(module)s:%(lineno)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        if not lg.hasHandlers():
            # logging to file
            path = PurePath(
                config.get('log_path'), config.get('name'))    
            handler = RotatingFileHandler(
                str(path),
                maxBytes=config.get('rotate_bytes'),
                backupCount=config.get('rotate_count'))
            handler.setLevel(config['file_level'])
            handler.setFormatter(formatter)
            lg.addHandler(handler)

            # logging to console
            handler = logging.StreamHandler()
            handler.setLevel(config['console_level'])
            handler.setFormatter(formatter)
            lg.addHandler(handler)
        return lg