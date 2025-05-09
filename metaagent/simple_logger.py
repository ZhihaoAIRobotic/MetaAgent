
import sys
import os
from loguru import logger as _logger

from metaagent.const import PROJECT_ROOT


def define_log_level(print_level="INFO", logfile_level="DEBUG"):
    """
       Adjust the log level to above level
    """
    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    # current working directory
    _logger.add(f'{os.getcwd()}/logs/log.txt', level=logfile_level)
    return _logger


logger = define_log_level()
