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

def send_alert(event, timestamp, severity):
    logger.info('Alert triggered: {},{},{}'.format(
        event['Type'],
        event['Action'],
        event['Actor']['ID']
    ))
    slack_alert.send(event=event, config=config, this_host=this_host, severity=severity, timestamp=timestamp)

def shutdown(_signo, _stack_frame):
  logger.info('Recieved {}, shutting down'.format(_signo))
  sys.exit(0)

def should_send_alert(event, config):
    event_actor_name = event['Actor']['Attributes']['name']
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
    ''' Look for any event on the event stream that matches the defined event types  '''
    for event in stream:
        if should_send_alert(event, config):
            event_type = event['Type']
            event_action = event['Action']
            timestamp = datetime.datetime.fromtimestamp(
                event['time']).strftime('%c')
            try:
                severity = config['events'][event_type][event_action]['severity']
                send_alert(event, timestamp, severity)
            except Exception as e:
                logger.error('Error sending alert: {}'.format(e))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    logger = log.load()
    config = conf.load()
    try:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        stream = client.events(decode=True)
        this_host = os.environ['HOST_NAME'] or 'docker-events'
    except:
        logger.info('Failed to connect to Docker event stream')
        sys.exit(1)
    
    if 'SLACK_WEBHOOK_URI' not in os.environ:
        logger.error('SLACK_WEBHOOK_URI env variable not set, exiting')
        sys.exit(1)

    logger.info('Starting up')
    main()
