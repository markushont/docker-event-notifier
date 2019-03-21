# Docker Event Notifier

Catch events from Docker daemon and send notifications (to Slack)

## Running in Docker

There are two environment variables to set:

* `HOST_NAME`: Name of host machine (optional). Used to label alerts
* `SLACK_WEBHOOK_URI`: URI to use when posting alerts in Slack

There are two volumes to be mounted:

* `/var/run/docker.sock`: Docker (Unix) socket at which to listen for events
* `/app/conf.json`: The configuration file (see next section)

Example Docker run command:

`docker run -e "HOST_NAME=foo_bar" -e "SLACK_WEBHOOK_URI=https://hooks.slack.com/services/XXX/YYY/ZZZ" -v /some_path/conf.json:/app/conf.json -v /var/run/docker.sock:/var/run/docker.sock docker-event-notifier`

## Configuration

The application is configured in `/app/conf.json`. The following sections can be included:

### Settings
* `logging`: Log level (debug, info warning, error)
* `tags`: Optional extra tags to include in alerts
* `mode = 'opt-in'|'opt-out'`: Opts in or out the containers that are listed in `names` below
* `names`: Names of containers to be either opted in or out

### Events
Builds upon the [Docker Events Documentation](https://docs.docker.com/engine/reference/commandline/events/). Is structured as

```json
{
    "events": {
        "object_type=container|image|network|etc": {
            "event_type=start|stop|die|etc": {
                "attributes": {
                    "attribute_x": "include_if_value"
                },
                "severity": "good|warning|danger"
            }
        }
    }
}
```

### Example
Below is an example of `/app/conf.json`:

```json
{
    "settings": {
        "logging": "info",
        "tags": [
            "foo-bar"
        ],
        "mode": "opt-out",
        "names": [
            "docker-events"
        ]
    },
    "events": {
        "container": {
            "die": {
                "attributes": {
                    "exitCode": "1"
                },
                "severity": "danger"
            },
            "stop": {
                "severity": "warning"
            },
            "start": {
                "severity": "good"
            }
        },
        "image": {
            "delete": {
                "severity": "warning"
            }
        }
    }
}
```