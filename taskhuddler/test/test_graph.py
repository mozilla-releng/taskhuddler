import pytest
from unittest.mock import patch

import os
import json
import datetime
import dateutil.parser
import tempfile

from taskhuddler.graph import TaskGraph
import taskcluster

TASK_IDS = [
    'A-8AqzvvRsqH9b0VHBXYjA',
    "A-aPcZanRJaxM-IToHyyHw",
    "A0BaQjdkS8Wdy2Ev_1pLgA",
    "A0VWjOkmRNqkKrRUj83BEA",
    "A0cabJ3WTeCrDN15nbTPYw",
]


def mocked_listTaskGroup(dummy, groupid, query):
    if 'continuationToken' in query:
        filename = "{}.json".format(query['continuationToken'])
    else:
        filename = 'completed.json'

    with open(os.path.join(os.path.dirname(__file__), 'data', filename)) as f:
        return json.loads(f.read())


def test_taskgraph_str():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert "{}".format(graph) == "<TaskGraph eShtp2faQgy4iZZOIhXvhw>"


def test_taskgraph_repr():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert repr(graph) == "<TaskGraph eShtp2faQgy4iZZOIhXvhw>"


def test_cache_file():
    tmpdir = tempfile.mkdtemp()
    os.environ['TC_CACHE_DIR'] = tmpdir
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        # and again to hit the cached copy.
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert repr(graph) == "<TaskGraph eShtp2faQgy4iZZOIhXvhw>"



@pytest.mark.parametrize('limit', [None, 2])
def test_taskgraph_tasks(limit):
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')

        found_taskids = list()
        for count, task in enumerate(graph.tasks(limit=limit), start=1):
            found_taskids.append(task.taskid)
        if limit:
            expected_task_ids = TASK_IDS[:limit]
        else:
            expected_task_ids = TASK_IDS

        assert found_taskids == expected_task_ids
        assert count == len(expected_task_ids)


def test_taskgraph_completed_bool():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert graph.completed is False


def test_graph_started():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert graph.earliest_start_time == dateutil.parser.parse('2017-10-26T01:03:59.291Z')


def test_graph_completed():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert graph.latest_finished_time == dateutil.parser.parse('2017-10-26T03:57:42.727Z')


def test_graph_states():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert graph.current_states() == {'completed': 3, 'failed': 1, 'unscheduled': 1}


def test_graph_total_compute_time():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert graph.total_compute_time() == datetime.timedelta(seconds=1120, microseconds=101000)


def test_graph_total_wall_time():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert graph.total_wall_time() == datetime.timedelta(seconds=10423, microseconds=436000)


def test_graph_total_compute_wall_time():
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw')
        assert graph.total_compute_wall_time() == datetime.timedelta(seconds=1048, microseconds=976000)
