import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(level:str="INFO", logfile:str="./logs/profit_analyzer.log",
                  max_bytes:int=1048576, backup_count:int=5):
    os.makedirs(os.path.dirname(logfile), exist_ok=True)
    logger = logging.getLogger("profit_analyzer")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers = []

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, level.upper(), logging.INFO))
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
    logger.addHandler(ch)

    # Rotating file
    fh = RotatingFileHandler(logfile, maxBytes=max_bytes, backupCount=backup_count)
    fh.setLevel(getattr(logging, level.upper(), logging.INFO))
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
    ))
    logger.addHandler(fh)

    logger.debug("Logger initialized")
    return logger
