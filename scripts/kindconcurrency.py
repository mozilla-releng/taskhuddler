"""
How many MAR signing tasks run concurrently?
"""

import asyncio
from datetime import datetime, timedelta
from dateutil import rrule

from taskhuddler.aio.nightly import load_nightly_graph
import pandas as pd


async def async_main():
    """Run all the async tasks."""

    graph = await load_nightly_graph(datetime.now() - timedelta(days=2))
    graph = graph['graph']

    signing_kinds = [k for k in graph.kinds if 'signing' in k]
    signing_tasks = [task for task in graph.filter_tasks_by_kind(kind='.*signing.*')]

    for kind in signing_kinds:
        print("{}: {}".format(kind, len([task for task in graph.tasks() if task.kind == kind])))

    task_type = {dt: {'timestamp': '{}'.format(dt), 'total': 0} for dt in rrule.rrule(
        rrule.MINUTELY, dtstart=graph.earliest_start_time, until=graph.latest_finished_time)}

    signing_type = {dt: {'timestamp': '{}'.format(dt), 'total': 0} for dt in rrule.rrule(
        rrule.MINUTELY, dtstart=graph.earliest_start_time, until=graph.latest_finished_time)}


    for task in signing_tasks:
        for bucket in task_type:
            bucket_end = bucket + timedelta(minutes=1)
            if task.started <= bucket_end and task.resolved >= bucket:
                if task.kind not in task_type[bucket]:
                    task_type[bucket][task.kind] = 0
                task_type[bucket][task.kind] += 1
                task_type[bucket]['total'] += 1

                for scope in task.scopes:
                    if 'signing:format' not in scope:
                        continue
                    scope = scope.split(':')[-1]
                    if scope not in signing_type[bucket]:
                        signing_type[bucket][scope] = 0
                    signing_type[bucket][scope] += 1
                    signing_type[bucket]['total'] += 1

    df = pd.DataFrame([task_type[r] for r in task_type])
    df2 = df.fillna(0)
    df2.to_csv('signing_by_task_type.csv')

    df3 = pd.DataFrame([signing_type[r] for r in signing_type]).fillna(0)
    df3.to_csv('signing_by_format.csv')

def main():
    """Manage the async loop."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
    loop.close()


if __name__ == '__main__':
    main()
