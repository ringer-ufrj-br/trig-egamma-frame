
import logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'streamFormat': {
            'format': '%(asctime)s - %(process)d - %(levelname)s - %(module)s '
            '- %(funcName)s - %(message)s'
        },
        'csvformat': {
            'format': '%(asctime)s;%(process)d;%(levelname)s;%(module)s;'
            '%(funcName)s;%(message)s'
        }
    },
    'handlers': {
        'stream': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'streamFormat',
        }
    },
    'loggers': {
        'trig-egamma-frame-debug': {
            'level': 'DEBUG',
            'handlers': ['stream'],
            'propagate': True
        }
    }
}


def set_loggers() -> logging.Logger:
    """
    Set the loggers for the package and returns the root logger

    Returns
    -------
    logging.Logger
        The root logger
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger()
