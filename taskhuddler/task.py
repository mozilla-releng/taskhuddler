"""class Task, to extract data about tasks."""

import dateutil.parser

from taskcluster import Queue

from .utils import tc_options


class Task(object):
    """Collected information about a single task."""

    def __init__(self, json=None, task_id=None, queue=None):
        """init."""
        self.queue = queue
        if not self.queue:
            self.queue = Queue(tc_options())
        if not json:
            json = dict()
        self.task = TaskDefinition(json=json.get('task'), task_id=task_id, queue=self.queue)
        self.status = TaskStatus(json=json.get('status'), task_id=task_id, queue=self.queue)
    # Properties to extract commonly used values.

    def __repr__(self):
        """repr."""
        return "<Task {}>".format(self.task_id)

    def __str__(self):
        """Str representation."""
        return "<Task {}:{}>".format(self.task_id, self.state)

    @property
    def json(self):
        """Reconstruct json as presented by listTaskGroup."""
        rv = dict()
        rv.update(self.status.json)
        rv.update(self.task.json)
        return rv

    @property
    def task_id(self):
        """Extract taskId."""
        return self.status.task_id

    @property
    def taskid(self):
        """Taskid for compatibility."""
        return self.task_id

    @property
    def label(self):
        """Extract label."""
        return self.task.label

    @property
    def state(self):
        """Return current task state."""
        return self.status.state

    @property
    def completed(self):
        """Return True if this task has completed."""
        return self.status.completed

    @property
    def scheduled(self):
        """Return datetime of the task scheduled time."""
        return self.status.scheduled

    @property
    def started(self):
        """Return datetime of the most recent run's start."""
        return self.status.started

    @property
    def resolved(self):
        """Return datetime of the most recent run's finish time."""
        return self.status.resolved

    def run_durations(self):
        """Return a list of timedelta objects, of run durations."""
        return self.status.run_durations()

    @property
    def kind(self):
        """Return the task's kind."""
        return self.task.kind

    @property
    def scopes(self):
        """Return a list of the scopes used, if any."""
        return self.task.scopes

    @property
    def has_failures(self):
        """Return True if this task has any run failures."""
        return self.status.has_failures

    @property
    def name(self):
        """Return the name of the task."""
        return self.task.name


class TaskDefinition:
    """Data and queries about a task definition."""

    def __init__(self, json=None, task_id=None, queue=None):
        """Init."""
        # taskId is not provided in the definition
        if task_id:
            self.task_id = task_id
        if json:
            self._json = json.get('task', json)
            return
        if not task_id:
            raise ValueError('No task definition or taskId provided')
        self.queue = queue
        if not self.queue:
            self.queue = Queue(tc_options())
        self._fetch_definition()

    def _fetch_definition(self):
        self._json = self.queue.task(self.task_id)

    def __repr__(self):
        """repr."""
        return "<TaskDefinition {}>".format(self.task_id)

    def __str__(self):
        """Str representation."""
        return "<TaskDefinition {}>".format(self.task_id)

    @property
    def json(self):
        """Return json as originally presented."""
        return {'task': self._json}

    @property
    def label(self):
        """Extract label."""
        return self._json.get('tags', {}).get(
            'label', self._json.get('metadata').get('name', '')
        )

    @property
    def kind(self):
        """Return the task's kind."""
        return self._json['tags'].get('kind', '')

    @property
    def scopes(self):
        """Return a list of the scopes used, if any."""
        return self._json.get('scopes', [])

    @property
    def name(self):
        """Return the name of the task."""
        return self._json['metadata']['name']


class TaskStatus:
    """Data and queries about a task status."""

    def __init__(self, json=None, task_id=None, queue=None):
        """Init."""
        if task_id:
            self.task_id = task_id
        if json:
            # We might be passed {'status': ... } or just the contents
            self._json = json.get('status', json)
            self.task_id = self._json['taskId']
            return
        if not task_id:
            raise ValueError('No task definition or taskId provided')
        self.queue = queue
        if not self.queue:
            self.queue = Queue(tc_options())
        self._fetch_status()

    def _fetch_status(self):
        json = self.queue.status(self.task_id)
        self._json = json.get('status', json)

    def __repr__(self):
        """repr."""
        return "<TaskStatus {}>".format(self.task_id)

    def __str__(self):
        """Str representation."""
        return "<TaskStatus {}:{}>".format(self.task_id, self.state)

    @property
    def json(self):
        """Return json as originally presented."""
        return {'status': self._json}

    @property
    def state(self):
        """Return current task state."""
        return self._json.get('state', '')

    @property
    def has_failures(self):
        """Return True if this task has any run failures."""
        return len([r for r in self._json.get('runs', list()) if r.get('state') in ['failed', 'exception']]) > 0

    @property
    def completed(self):
        """Return True if this task has completed.

        Returns: Bool
            if the highest runId has state 'completed'

        """
        return self.state == 'completed'

    def _extract_date(self, run_field, run_id=-1):
        """Return datetime of the given field in the task runs."""
        if not self._json.get('runs'):
            return
        field_data = self._json['runs'][run_id].get(run_field)
        if not field_data:
            return
        return dateutil.parser.parse(field_data)

    @property
    def scheduled(self):
        """Return datetime of the task scheduled time."""
        if self.state == 'unscheduled':
            return
        return self._extract_date('scheduled')

    @property
    def started(self):
        """Return datetime of the most recent run's start."""
        return self._extract_date('started')

    @property
    def resolved(self):
        """Return datetime of the most recent run's finish time."""
        return self._extract_date('resolved')

    def run_durations(self):
        """Return a list of timedelta objects, of run durations."""
        durations = list()
        if not self.json['status'].get('runs'):
            return durations
        for run in self._json.get('runs', list()):
            started = run.get('started')
            resolved = run.get('resolved')
            if started and resolved:
                durations.append(dateutil.parser.parse(resolved) - dateutil.parser.parse(started))
        return durations
