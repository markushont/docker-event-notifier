import json
import logging
import sys

def load():
    # Load config from file
    try:
        logger = logging.getLogger('main')
        config = json.load(open('conf.json', 'r'))
    except Exception as e:
        logger.error('Unable to load configuration - shutting down. Error: %s ' % e)
        sys.exit(1)

    # Validate config
    if config:
        # Settings
        if 'settings' in config:
            if 'logging' not in config['settings']:
                config['settings']['logging'] = 'info'
            if 'mode' not in config['settings']:
                config['settings']['mode'] = 'opt-out'
        else:
            logger.warn('Settings not defined - loading defaults')
            config['settings'] = {'logging': 'info'}
        # Events
        if 'events' in config:
            pass
        else:
            logger.warn(
                'No events have been specified so no alerts will be triggered')
            config['events'] = {}
        # Return
        return config
    else:
        logger.error('Unable to load configuration - shutting down')
        sys.exit(1)
