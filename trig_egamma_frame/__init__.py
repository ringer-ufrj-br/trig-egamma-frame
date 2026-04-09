__all__ = []

import sys
from loguru         import logger
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
