from loguru import logger
from pathlib import Path
from functools import reduce

class MyLogger(object):
    @staticmethod
    def path(*args) -> str:
        res = reduce(lambda a, b: Path(a) / b, args)
        return str(res)

    def __init__(self, log_file: str = './log/', rotation: int = "4 MB", retention: int = "7 days"):
        self.logger = logger
        self.logger.add(MyLogger.path(log_file + "Info_{time:YYYY-MM-DD}.log"), rotation=rotation, retention=retention,
                        level="INFO")
        self.logger.add(MyLogger.path(log_file + "Error.log"), rotation="8 MB", retention="30 days", level="ERROR")
        self.logger.add(MyLogger.path(log_file + "Debug.log"), rotation="32 MB", retention="3 days", level="DEBUG")

    def get_logger(self):
        return self.logger


mylog: logger = MyLogger().get_logger()
