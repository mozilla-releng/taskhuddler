"""Helpful wrapper around release related taskcluster operations."""

import logging
import taskcluster
from .task import Task

log = logging.getLogger(__name__)


class TaskGraph(object):
    """docstring for TaskGraph."""

    def __init__(self, groupid, caching=False):
        """Init."""
        self.groupid = groupid
        self.queue = taskcluster.Queue()
        if caching:
            self.refresh_task_cache()
        else:
            self.tasklist = []

    def refresh_task_cache(self):
        """Refresh the local task cache."""
        self.tasklist = [Task(json=data) for data in self._tasks_live(as_json=True)]

    def _tasks_cached(self, limit=None):
        """Return the tasks from the local cache"""
        if not self.tasklist:
            self.refresh_task_cache()
        for count, task in enumerate(self.tasklist, 1):
            if limit and count > limit:
                break
            yield task

    def _tasks_live(self, limit=None, as_json=False):
        """
        Return tasks with the associated group ID.

        Handles continuationToken without the user being aware of it.

        Enforces the limit parameter as a limit of the total number of tasks
        to be returned.
        """

        query = {}
        if limit:
            # Default taskcluster-client api asks for 1000 tasks.
            query['limit'] = min(limit, 1000)

        outcome = self.queue.listTaskGroup(self.groupid, query=query)
        tasks = outcome.get('tasks', [])

        for yielded, task in enumerate(tasks, 1):
            if limit and yielded > limit:
                break
            # If we've run out of tasks from this response, but still have more
            # to fetch
            if len(tasks) == yielded and outcome.get('continuationToken'):
                query.update({
                    'continuationToken': outcome.get('continuationToken')
                })
                outcome = self.queue.listTaskGroup(self.groupid, query=query)
                tasks.extend(outcome.get('tasks', []))
            if as_json:
                yield task
            else:
                yield Task(json=task)

    def tasks(self, limit=None, use_cache=None):
        if not use_cache:
            use_cache = True if self.tasklist else False

        if use_cache:
            return self._tasks_cached(limit=limit)
        else:
            return self._tasks_live(limit=limit, as_json=False)

    @property
    def completed(self):
        """Have all the tasks completed

        Returns bool.
        """
        return all([task.completed for task in self.tasks()])

    @property
    def earliest_start_time(self):
        """Return the earliest start time for any task in the graph
        that has actually started"""
        return min([task.started for task in self.tasks() if task.started])

    @property
    def latest_finished_time(self):
        """Return the latest finish time for any task in the graph
        that has one"""
        return max([task.resolved for task in self.tasks() if task.resolved])
