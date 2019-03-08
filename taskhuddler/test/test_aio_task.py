import pytest
from unittest.mock import patch

import os
import json
import datetime
import dateutil.parser
import tempfile

from taskhuddler.aio import Task, TaskDefinition, TaskStatus
import taskcluster


async def mocked_status(dummy, task_id):
    return get_dummy_task_status('completed.json')


async def mocked_definition(dummy, task_id):
    return get_dummy_task_definition('completed.json')


def get_dummy_task_json(filename):
    with open(os.path.join(os.path.dirname(__file__), 'data', filename)) as f:
        return json.loads(f.read()).get('tasks')[0]


def get_dummy_task_status(filename):
    full = get_dummy_task_json(filename)
    return full.get('status')


def get_dummy_task_definition(filename):
    full = get_dummy_task_json(filename)
    return full.get('task')


@pytest.mark.asyncio
async def test_task_str():
    with patch.object(taskcluster.aio.Queue, 'status', new=mocked_status) as mocked_method, patch.object(taskcluster.aio.Queue, 'task', new=mocked_definition) as mocked_method2:
        task = await Task(task_id='A-8AqzvvRsqH9b0VHBXYjA')
        assert "{}".format(task) == "<Task A-8AqzvvRsqH9b0VHBXYjA:completed>"
        assert repr(task) == "<Task A-8AqzvvRsqH9b0VHBXYjA>"


@pytest.mark.asyncio
async def test_taskstatus_str():
    with patch.object(taskcluster.aio.Queue, 'status', new=mocked_status) as mocked_method:
        task = await TaskStatus(task_id='A-8AqzvvRsqH9b0VHBXYjA')
        assert "{}".format(task) == "<TaskStatus A-8AqzvvRsqH9b0VHBXYjA:completed>"
        assert repr(task) == "<TaskStatus A-8AqzvvRsqH9b0VHBXYjA>"


@pytest.mark.asyncio
async def test_taskdef_str():
    with patch.object(taskcluster.aio.Queue, 'task', new=mocked_definition) as mocked_method:
        task = await TaskDefinition(task_id='A-8AqzvvRsqH9b0VHBXYjA')
        assert "{}".format(task) == "<TaskDefinition A-8AqzvvRsqH9b0VHBXYjA>"
        assert repr(task) == "<TaskDefinition A-8AqzvvRsqH9b0VHBXYjA>"
