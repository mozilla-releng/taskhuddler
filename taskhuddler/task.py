
import dateutil.parser


class Task(object):
    """docstring for Task."""

    def __init__(self, json=None):
        self.json = json

    # Properties to extract commonly used values.

    @property
    def taskid(self):
        return self.json['status']['taskId']

    @property
    def state(self):
        return self.json['status'].get('state', '')

    @property
    def completed(self):
        """Has this task completed.

        Returns: Bool
            if the highest runId has state 'completed'
        """
        return self.state == 'completed'

    @property
    def scheduled(self):
        """What time did the most recent run get scheduled?
        (aka: what time did it move from unscheduled to pending?)
        Field looks like:
        "scheduled": "2017-10-26T01:03:59.291Z",
        Returns: datetime object of start time, or None if not applicable
        """
        if not self.json['status'].get('runs'):
            return
        scheduled = self.json['status']['runs'][-1].get('scheduled')
        if not scheduled:
            return
        return dateutil.parser.parse(scheduled)

    @property
    def started(self):
        """What time did the most recent run start?
        Field looks like:
        "started": "2017-10-26T01:03:59.291Z",
        Returns: datetime object of start time, or None if not applicable
        """
        if not self.json['status'].get('runs'):
            return
        started = self.json['status']['runs'][-1].get('started')
        if not started:
            return
        return dateutil.parser.parse(started)

    @property
    def resolved(self):
        """What time did the most recent run finish?
        Field looks like:
        "resolved": "2017-10-26T01:03:59.291Z",
        Returns: datetime object of resolved time, or None if not applicable
        """
        if not self.json['status'].get('runs'):
            return
        resolved = self.json['status']['runs'][-1].get('resolved')
        if not resolved:
            return
        return dateutil.parser.parse(resolved)
