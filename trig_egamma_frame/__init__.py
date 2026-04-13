__all__ = []

import sys
from loguru         import logger as _logger
from rich_argparse  import RichHelpFormatter

def get_argparser_formatter():
    RichHelpFormatter.styles["argparse.args"]     = "green"
    RichHelpFormatter.styles["argparse.prog"]     = "bold grey50"
    RichHelpFormatter.styles["argparse.groups"]   = "bold green"
    RichHelpFormatter.styles["argparse.help"]     = "grey50"
    RichHelpFormatter.styles["argparse.metavar"]  = "blue"
    return RichHelpFormatter

def setup_logs( name , level="INFO"):
    """Setup and configure the logger"""
    logger.configure(extra={"name" : name})
    logger.remove()  # Remove any old handler
    #format="<green>{time:DD-MMM-YYYY HH:mm:ss}</green> | <level>{level:^12}</level> | <cyan>{extra[slurms_name]:<30}</cyan> | <blue>{message}</blue>"
    if level=="DEBUG":
        format="<blue>{time:DD-MMM-YYYY HH:mm:ss}</blue> | <level>{level:^12}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> |{message}"
    else:
        format="<blue>{time:DD-MMM-YYYY HH:mm:ss}</blue> | {message}"
    logger.add(
        sys.stdout,
        colorize=True,
        backtrace=True,
        diagnose=True,
        level=level,
        format=format,
    )

def _fatal(logger_inst, message, *args, **kwargs):
    """
    Custom fatal method for loguru logger.
    It logs at FATAL level and raises an exception.
    Usage:
        logger.fatal("Message")
        logger.fatal("Message with %s", arg)
        logger.fatal("Message", ValueError)
        logger.fatal("Message with %s", arg, ValueError)
    """
    # 1. Determine if the last arg is an exception class
    exc_type = RuntimeError
    largs = list(args)
    if largs and isinstance(largs[-1], type) and issubclass(largs[-1], Exception):
        exc_type = largs.pop()
    
    # 2. Format the message if there are remaining args
    if largs:
        try:
            if "%" in message:
                formatted_msg = message % tuple(largs)
            else:
                formatted_msg = f"{message} {largs}"
        except:
             formatted_msg = f"{message} {largs}"
    else:
        formatted_msg = message
        
    # 3. Log it
    # depth=2 to skip this function AND the LoggerWrapper.fatal call
    logger_inst.opt(depth=2).log("FATAL", formatted_msg, **kwargs)
    
    # 4. Raise
    raise exc_type(formatted_msg)

# Register FATAL level
try:
    _logger.level("FATAL", no=60, color="<red><bold>")
except TypeError: # Level already exists
    pass

# Patch logger to include fatal method
# Note: Since we can't easily add methods to the loguru logger proxy directly, 
# we provide a wrapped version that handles chained calls.
class LoggerWrapper:
    def __init__(self, logger_obj):
        self._logger = logger_obj
    def __getattr__(self, name):
        attr = getattr(self._logger, name)
        # Wrap methods that return a new logger instance
        if name in ("bind", "opt", "patch", "configure"):
            def wrapper(*args, **kwargs):
                return LoggerWrapper(attr(*args, **kwargs))
            return wrapper
        return attr
    def fatal(self, *args, **kwargs):
        return _fatal(self._logger, *args, **kwargs)

logger = LoggerWrapper(_logger)
    
from . import enumerators
__all__.extend(enumerators.__all__)
from .enumerators import *

from . import constants
__all__.extend(constants.__all__)
from .constants import *

from . import exceptions
__all__.extend(exceptions.__all__)
from .exceptions import *

from . import kernel
__all__.extend(kernel.__all__)
from .kernel import *

from . import dataframe
__all__.extend(dataframe.__all__)
from .dataframe import *

from . import event
__all__.extend(event.__all__)
from .event import *

from . import emulator
__all__.extend(emulator.__all__)
from .emulator import *

from . import algorithms
__all__.extend(algorithms.__all__)
from .algorithms import *


