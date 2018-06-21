"""class Task, to extract data about tasks."""

import dateutil.parser


class Task(object):
    """docstring for Task."""

    def __init__(self, json=None):
        self.json = json

    # Properties to extract commonly used values.

    @property
    def taskid(self):
        """Extract taskid."""
        return self.json['status']['taskId']

    @property
    def state(self):
        """Current task state."""
        return self.json['status'].get('state', '')

    @property
    def completed(self):
        """True if this task has completed.

        Returns: Bool
            if the highest runId has state 'completed'
        """
        return self.state == 'completed'

    @property
    def scheduled(self):
        """Returns datetime of the task scheduled time.

        What time did it move from unscheduled to pending?
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
        """Returns datetime of the most recent run's start

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
        """Returns datetime of the most recent run's finish time.

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

    @property
    def kind(self):
        """Returns the task's kind."""
        if 'kind' in self.json['task']['tags']:
            return self.json['task']['tags']['kind']
        # probably the decision task, if no kind
        return ''

    @property
    def scopes(self):
        return self.json['task'].get('scopes', [])
