import conf
import datetime
import docker
import json
import log
import os
import signal
import slack_alert
import sys
import time

def send_alerts(events):
    if len(events) == 0:
        return
    logger.info('Found %d relevant events' % len(events))
    slack_alert.batch_send(events, config, this_host)

def shutdown(_signo, _stack_frame):
  logger.info('Recieved {}, shutting down'.format(_signo))
  sys.exit(0)

def should_send_alert(event, config):
    event_actor_name = event['Actor']['Attributes']['name'] if 'name' in event['Actor']['Attributes'] else ''
    name_in_config = event_actor_name in config['settings']['names']
    event_type = event['Type']
    event_action = event['Action']

    # Does not match mode
    if 'opt-in' in config['settings']['mode'] and not name_in_config:
        return False
    if 'opt-out' in config['settings']['mode'] and name_in_config:
        return False

    # Has no settings
    if event_type not in config['events'] or event_action not in config['events'][event_type]:
        return False

    # Does not match attributes
    actor_attributes = event['Actor']['Attributes']
    if 'attributes' in config['events'][event_type]:
        # Go through attributes if configured
        config_attributes = config['events'][event_type]['attributes']
        for attribute in config_attributes:
            if actor_attributes[attribute] != config[attribute]:
                return False
    
    return True   

def main():
    while True:
        time.sleep(config['settings']['check_interval'])

        ''' Look for any event on the event stream that matches the defined event types  '''
        logger.info('Checking for new events')
        events = []
        now = int(time.time())
        then = now - config['settings']['check_interval']
        stream = client.events(since=then, until=now, decode=True)
        for event in stream:
            if should_send_alert(event, config):
                event_type = event['Type']
                event_action = event['Action']
                timestamp = datetime.datetime.fromtimestamp(
                    event['time']).strftime('%c')
                severity = config['events'][event_type][event_action]['severity'] or 'good'
                events.append({
                    'event': event,
                    'timestamp': timestamp,
                    'severity': severity
                })
        send_alerts(events)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    logger = log.load()
    config = conf.load()
    try:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        this_host = os.environ['HOST_NAME'] or 'docker-events'
    except:
        logger.info('Failed to connect to Docker event stream')
        sys.exit(1)
    
    if 'SLACK_WEBHOOK_URI' not in os.environ:
        logger.error('SLACK_WEBHOOK_URI env variable not set, exiting')
        sys.exit(1)

    logger.info('Starting up')
    main()
