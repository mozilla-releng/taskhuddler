"""Helpful wrapper around release related taskcluster operations."""

import logging

from asyncinit import asyncinit
from taskcluster.aio import Queue
from taskhuddler.task import TaskDefinition as SyncTaskDefinition
from taskhuddler.task import TaskStatus as SyncTaskStatus
from taskhuddler.utils import tc_options

log = logging.getLogger(__name__)


@asyncinit
class TaskDefinition(SyncTaskDefinition):
    """Helper class for dealing with Tasks, asyncio version."""

    async def __init__(self, json=None, task_id=None, queue=None):
        """Init."""
        # taskId is not provided in the definition
        if task_id:
            self.task_id = task_id
        if json:
            self.def_json = json.get('task', json)
            return
        if not task_id:
            raise ValueError('No task definition or taskId provided')
        self.queue = queue
        if not self.queue:
            self.queue = Queue(tc_options())
        await self._fetch_definition()

    async def _fetch_definition(self):
        self.def_json = await self.queue.task(self.task_id)


@asyncinit
class TaskStatus(SyncTaskStatus):
    """Helper class for dealing with Tasks, asyncio version."""

    async def __init__(self, json=None, task_id=None, queue=None):
        """Init."""
        if task_id:
            self.task_id = task_id
        if json:
            # We might be passed {'status': ... } or just the contents
            self.status_json = json.get('status', json)
            self.task_id = self.status_json['taskId']
            return
        if not task_id:
            raise ValueError('No task definition or taskId provided')
        self.queue = queue
        if not self.queue:
            self.queue = Queue(tc_options())
        await self._fetch_status()

    async def _fetch_status(self):
        json = await self.queue.status(self.task_id)
        self.status_json = json.get('status', json)


@asyncinit
class Task(TaskDefinition, TaskStatus):
    """Helper class for dealing with Tasks, asyncio version."""

    async def __init__(self, json=None, task_id=None, queue=None):
        """init."""
        if json:
            self.def_json = json.get('task')
            self.status_json = json.get('status')
            self.task_id = self.status_json['taskId']
            return

        if task_id:
            self.task_id = task_id
        else:
            raise ValueError('No task definition or taskId provided')
        self.queue = queue
        if not self.queue:
            self.queue = Queue(tc_options())
        if self.task_id:
            await self._fetch_definition()
            await self._fetch_status()

    def __repr__(self):
        """repr."""
        return "<Task {}>".format(self.task_id)

    def __str__(self):
        """Str representation."""
        return "<Task {}:{}>".format(self.task_id, self.state)
