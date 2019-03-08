"""Extract useful information from Nightly taskgraphs."""

import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
from taskcluster.aio import Index, Queue
from taskhuddler.aio.graph import TaskGraph
from taskhuddler.utils import tc_options

log = logging.getLogger(__name__)

VALID_PLATFORMS = [
    'linux-opt',
    'linux64-opt',
    'macosx64-opt',
    'win32-opt',
    'win64-opt'
]


async def load_nightly_graph(dt=None, platform='linux-opt'):
    """Given a date, load the relevant nightly task graph."""
    async with aiohttp.ClientSession() as session:
        index = Index(options=tc_options(), session=session)
        queue = Queue(options=tc_options(), session=session)

        if not dt:
            dt = datetime.now()

        datestr = dt.strftime("%Y.%m.%d")
        basestr = "gecko.v2.mozilla-central.nightly.{date}.latest.firefox.{platform}"
        found = await index.findTask(basestr.format(date=datestr, platform=platform))
        taskid = found.get('taskId')

        taskdef = await queue.task(taskid)
        # except taskcluster.exceptions.TaskclusterRestFailure:

        taskgroup = taskdef.get('taskGroupId')
        log.debug("Looking at {} for {}".format(taskgroup, datestr))
        if taskgroup:
            return {'date': datestr, 'graph': await TaskGraph(taskgroup)}

    return None


async def find_nightly_graphs(start=None, end=None, platform='linux-opt'):
    """Return a dict of nightly TaskGraphs between the provided dates."""
    if not start:
        start = datetime.now() - timedelta(1)
    if not end:
        end = datetime.now()

    current = end

    tasks = list()

    while current > start:
        log.info("Looking at {}".format(current))
        current = current - timedelta(1)
        tasks.append(asyncio.ensure_future(load_nightly_graph(current)))
    results = await asyncio.gather(*tasks)

    return {r['date']: r['graph'] for r in results if r}
