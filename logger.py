import logging
DEFAULT_LOG_LEVEL = logging.DEBUG

# create logger with 'spam_application'
logger = logging.getLogger('LaVidaModerna_Bot')
logger.setLevel(DEFAULT_LOG_LEVEL)
# create file handler which logs even debug messages
fh = logging.FileHandler('LaVidaModerna_Bot.log')
fh.setLevel(DEFAULT_LOG_LEVEL)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(DEFAULT_LOG_LEVEL)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def set_log_level(verbosity):
    numeric_level = get_numeric_log_level(verbosity)
    for c_logger in logger.handlers:
        c_logger.setLevel(numeric_level)


def get_numeric_log_level(verbosity):
    numeric_level = getattr(logging, verbosity.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % verbosity)
    return numeric_level


def get_logger(name):
    return logging.getLogger(name)