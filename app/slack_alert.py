import json
import logging
import os
import requests
import socket
import time

''' Send one event with details '''
def send(event, config, this_host, severity, timestamp):
    logger = logging.getLogger('main')

    # Define payload
    payload = {
        'username': 'Docker Event Notifier',
        'attachments': [
            {
                'fallback': 'Docker event triggered on *%s*' % this_host,
                'pretext': 'Docker event triggered on *%s*' % this_host,
                'color': severity,
                'fields': [
                    {
                        'title': 'Type',
                        'value': event['Type'],
                        'short': True
                    },
                    {
                        'title': 'Time',
                        'value': timestamp,
                        'short': True
                    },
                    {
                        'title': 'Action',
                        'value': event['Action'],
                        'short': True
                    },
                    {
                        'title': 'ID',
                        'value': event['Actor']['ID'][0:12],
                        'short': True
                    }
                ]
            }
        ]
    }

    # Append name to payload if exists
    if 'name' in event['Actor']['Attributes']:
        name_field = {
            'title': 'Name',
            'value': event['Actor']['Attributes']['name'],
            'short': False
        }
        payload['attachments'][0]['fields'].append(name_field)

    # Append tags to payload if exists
    if 'tags' in config['settings'] and len(config['settings']['tags']):
        tags = ', '.join([str(x) for x in config['settings']['tags']])
        tags_field = {
            'title': 'Tags',
            'value': tags,
            'short': False
        }
        payload['attachments'][0]['fields'].append(tags_field)

    logger.info('Event: %s' % json.dumps(payload))

    if 'SLACK_WEBHOOK_CHANNEL_ID' in os.environ:
        payload['channel'] = os.environ['SLACK_WEBHOOK_CHANNEL_ID']

    if 'SLACK_WEBHOOK_URI' in os.environ:
        # Perform request
        try:
            requests.post(
                os.environ['SLACK_WEBHOOK_URI'],
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
        except requests.exceptions.RequestException as e:
            logger.error('{}: {}'.format(__name__, e))

''' Batch send list of events '''
def batch_send(event_infos, config, this_host):
    logger = logging.getLogger('main')

    payload = {
        'username': 'Docker Event Notifier',
        'text': 'Docker events triggered on *%s*.' % this_host,
        'attachments': []
    }

    if 'tags' in config['settings'] and len(config['settings']['tags']):
        tags = ', '.join([str(x) for x in config['settings']['tags']])
        payload['text'] += '\n*Tags:* %s' % tags

    for event_info in event_infos:
        event = event_info['event']
        payload['attachments'].append({
            'fallback': event['Actor']['Attributes']['name'] if 'name' in event['Actor']['Attributes'] else 'Event',
            'color': event_info['severity'],
            'text': '{} *{}* at {}: *{}*'.format(
                event['Type'],
                event['Actor']['Attributes']['name'],
                event_info['timestamp'],
                event['Action']
            )
        })

    if 'SLACK_WEBHOOK_CHANNEL_ID' in os.environ:
        payload['channel'] = os.environ['SLACK_WEBHOOK_CHANNEL_ID']

    if 'SLACK_WEBHOOK_URI' in os.environ:
        # Perform request
        try:
            requests.post(
                os.environ['SLACK_WEBHOOK_URI'],
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
        except requests.exceptions.RequestException as e:
            logger.error('{}: {}'.format(__name__, e))
