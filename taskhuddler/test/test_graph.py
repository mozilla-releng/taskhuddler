import pytest
from unittest.mock import patch

import os
import json

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


@pytest.mark.parametrize('caching', [False, True])
@pytest.mark.parametrize('limit', [None, 2])
@pytest.mark.parametrize('use_cache', [False, True])
def test_taskgraph_tasks(caching, limit, use_cache):
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw', caching=caching)

        found_taskids = list()
        for count, task in enumerate(graph.tasks(limit=limit, use_cache=use_cache), start=1):
            found_taskids.append(task['status']['taskId'])
        if limit:
            expected_task_ids = TASK_IDS[:limit]
        else:
            expected_task_ids = TASK_IDS

        assert found_taskids == expected_task_ids
        assert count == len(expected_task_ids)


@pytest.mark.parametrize('caching', [False, True])
def test_taskgraph_completed_bool(caching):
    with patch.object(taskcluster.Queue, 'listTaskGroup', new=mocked_listTaskGroup) as mocked_method:
        graph = TaskGraph('eShtp2faQgy4iZZOIhXvhw', caching=caching)
        assert graph.completed is False
