import conf
import logging
import sys

def load():
    config = conf.load()
    logger = logging.getLogger('main')

    if 'logging' in config['settings']:
        level = config['settings']['logging']
        if level == 'debug':
            logger.setLevel(logging.DEBUG)
        if level == 'info':
            logger.setLevel(logging.INFO)
        if level == 'warn':
            logger.setLevel(logging.WARN)
        if level == 'error':
            logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%d-%m-%Y %I:%M:%S')
    # Everything <= WARN written to stdout
    ch1 = logging.StreamHandler(sys.stdout)
    ch1.setLevel(logging.DEBUG)
    ch1.addFilter(lambda record: record.levelno <= logging.WARN)
    ch1.setFormatter(formatter)
    # Everything == ERROR written to stderr
    ch2 = logging.StreamHandler(sys.stderr)
    ch2.setLevel(logging.ERROR)
    ch2.setFormatter(formatter)

    logger.addHandler(ch1)
    logger.addHandler(ch2)
    return logger
