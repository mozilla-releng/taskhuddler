"""class Task, to extract data about tasks."""

import dateutil.parser


class Task(object):
    """docstring for Task."""

    def __init__(self, json=None):
        """init."""
        self.json = json

    # Properties to extract commonly used values.

    @property
    def taskid(self):
        """Extract taskid."""
        return self.json['status']['taskId']

    @property
    def label(self):
        """Extract label."""
        return self.json['task'].get('tags', {}).get(
            'label', self.json['task'].get('metadata').get('name', '')
        )

    @property
    def state(self):
        """Return current task state."""
        return self.json['status'].get('state', '')

    @property
    def completed(self):
        """Return True if this task has completed.

        Returns: Bool
            if the highest runId has state 'completed'

        """
        return self.state == 'completed'

    @property
    def scheduled(self):
        """Return datetime of the task scheduled time.

        What time did it move from unscheduled to pending?
        Field looks like:
        "scheduled": "2017-10-26T01:03:59.291Z",
        Returns: datetime object of start time, or None if not applicable

        """
        if self.state == 'unscheduled' or not self.json['status'].get('runs'):
            return
        scheduled = self.json['status']['runs'][-1].get('scheduled')
        # if there's a run, then it's scheduled.
        return dateutil.parser.parse(scheduled)

    @property
    def started(self):
        """Return datetime of the most recent run's start.

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
        """Return datetime of the most recent run's finish time.

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

    def run_durations(self):
        """Return a list of timedelta objects, of run durations."""
        if not self.json['status'].get('runs'):
            return list()
        durations = list()
        for run in self.json['status'].get('runs', list()):
            started = run.get('started')
            resolved = run.get('resolved')
            if started and resolved:
                durations.append(dateutil.parser.parse(resolved) - dateutil.parser.parse(started))
        return durations

    @property
    def kind(self):
        """Return the task's kind."""
        return self.json['task']['tags'].get('kind', '')

    @property
    def scopes(self):
        """Return a list of the scopes used, if any."""
        return self.json['task'].get('scopes', [])

    @property
    def has_failures(self):
        """Return True if this task has any run failures."""
        return len([r for r in self.json['status'].get('runs', list()) if r.get('state') in ['failed', 'exception']]) > 0

    @property
    def name(self):
        """Return the name of the task."""
        return self.json['task']['metadata']['name']
