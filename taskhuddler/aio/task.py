"""Helpful wrapper around release related taskcluster operations."""

import logging

from asyncinit import asyncinit
from taskcluster.aio import Queue
from taskhuddler.task import Task as SyncTask
from taskhuddler.task import TaskDefinition as SyncTaskDefinition
from taskhuddler.task import TaskStatus as SyncTaskStatus
from taskhuddler.utils import tc_options

log = logging.getLogger(__name__)


@asyncinit
class Task(SyncTask):
    """Helper class for dealing with Tasks, asyncio version."""

    async def __init__(self, json=None, task_id=None, queue=None):
        """init."""
        self.queue = queue
        if not self.queue:
            self.queue = Queue(tc_options())
        if not json:
            json = dict()
        self.task = await TaskDefinition(json=json.get('task'), task_id=task_id, queue=self.queue)
        self.status = await TaskStatus(json=json.get('status'), task_id=task_id, queue=self.queue)


@asyncinit
class TaskDefinition(SyncTaskDefinition):
    """Helper class for dealing with Tasks, asyncio version."""

    async def __init__(self, json=None, task_id=None, queue=None):
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
        await self._fetch_definition()

    async def _fetch_definition(self):
        self._json = await self.queue.task(self.task_id)


@asyncinit
class TaskStatus(SyncTaskStatus):
    """Helper class for dealing with Tasks, asyncio version."""

    async def __init__(self, json=None, task_id=None, queue=None):
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
        await self._fetch_status()

    async def _fetch_status(self):
        json = await self.queue.status(self.task_id)
        self._json = json.get('status', json)
