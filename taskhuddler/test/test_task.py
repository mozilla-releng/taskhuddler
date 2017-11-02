"""Test Task class."""

import os
import json
import pytest

from taskhuddler.task import Task


def get_dummy_task_json(filename):
    with open(os.path.join(os.path.dirname(__file__), 'data', filename)) as f:
        return json.loads(f.read()).get('tasks')[0]


def test_task_taskid():
    task = Task(json=get_dummy_task_json('completed.json'))
    assert task.taskid == "A-8AqzvvRsqH9b0VHBXYjA"


@pytest.mark.parametrize('filename,state', (
    ['completed.json', True],
    ['unscheduled.json', False],
    ['failed.json', False]
))
def test_task_completed_bool(filename, state):
    task = Task(json=get_dummy_task_json(filename))
    assert task.completed is state


@pytest.mark.parametrize('filename,expected', (
    ['completed.json', 'completed'],
    ['unscheduled.json', 'unscheduled'],
    ['failed.json', 'failed']
))
def test_task_state_completed(filename, expected):
    task = Task(json=get_dummy_task_json(filename))
    assert task.state == expected
