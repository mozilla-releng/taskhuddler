"""Helpful wrapper around release related taskcluster operations."""

import logging
from collections import defaultdict
from taskcluster.async import Queue
import datetime
from taskhuddler.task import Task
from taskhuddler.utils import merge_date_list, Range
from asyncinit import asyncinit
import aiohttp

log = logging.getLogger(__name__)


@asyncinit
class TaskGraph(object):
    """Helper class for dealing with Task Graphs."""

    async def __init__(self, groupid):
        """init."""
        self.groupid = groupid
        self.tasklist = None
        await self.refresh_task_cache()

    def __repr__(self):
        return "<TaskGraph {}>".format(self.groupid)

    def __str__(self):
        return "<TaskGraph {}>".format(self.groupid)

    async def refresh_task_cache(self, limit=None):
        """Return tasks with the associated group ID.

        Handles continuationToken without the user being aware of it.

        Enforces the limit parameter as a limit of the total number of tasks
        to be returned.
        """
        query = {}
        if limit:
            # Default taskcluster-client api asks for 1000 tasks.
            query['limit'] = min(limit, 1000)

        def under_limit(length):
            """Indicate if we've returned enough tasks."""
            if not limit or length < limit:
                return True
            return False

        with aiohttp.ClientSession() as session:
            queue = Queue(session=session)
            outcome = await queue.listTaskGroup(self.groupid, query=query)
            tasks = outcome.get('tasks', [])

            while under_limit(len(tasks)) and outcome.get('continuationToken'):
                query.update({
                    'continuationToken': outcome.get('continuationToken')
                })
                outcome = await queue.listTaskGroup(self.groupid, query=query)
                tasks.extend(outcome.get('tasks', []))

            if limit:
                tasks = tasks[:limit]
            self.tasklist = [Task(json=data) for data in tasks]

    def tasks(self, limit=None, as_json=False):
        """Return all tasks in the graph."""
        if as_json:
            return [t.json for t in self.tasklist[:limit]]
        else:
            return self.tasklist[:limit]

    @property
    def completed(self):
        """Have all the tasks completed.

        Returns bool.
        """
        return all([task.completed for task in self.tasks()])

    def current_states(self):
        """Count the occurences of current states."""
        states = defaultdict(int)
        for state in [task.state for task in self.tasks()]:
            states[state] += 1
        return states

    @property
    def earliest_start_time(self):
        """Find the earliest start time for any task in the graph."""
        return min([task.started for task in self.tasks() if task.started])

    @property
    def latest_finished_time(self):
        """Find the latest finish time for resolved tasks."""
        return max([task.resolved for task in self.tasks() if task.resolved])

    def total_compute_time(self):
        """Sum of all the task run times, as timedelta."""
        return sum([task.resolved - task.started for task in self.tasks() if task.completed], datetime.timedelta(0, 0))

    def total_wall_time(self):
        """Return the total wall time for this graph.

        May not be a useful value if human decision tasks exist
        """
        return self.latest_finished_time - self.earliest_start_time

    def total_compute_wall_time(self):
        """Return the total time spent running tasks, ignoring wait times."""
        dt_list = [Range(start=task.started, end=task.resolved)
                   for task in self.tasks() if task.completed]
        merged = merge_date_list(dt_list)
        return sum([m.end - m.start for m in merged], datetime.timedelta(0, 0))

    def task_timings(self):
        """For every finished task that has fields we group on, report duration."""
        for task in self.tasklist:
            if not task.completed:
                continue
            try:
                kind = task.json['task']['tags']['kind']
                platform = task.json['task']['extra']['treeherder']['machine']['platform']
            except KeyError:
                continue
            yield {
                'kind': kind,
                'platform': platform,
                'duration': (task.resolved - task.started).seconds
            }
