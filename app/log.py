import conf
import logging

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

    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%d-%m-%Y %I:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
