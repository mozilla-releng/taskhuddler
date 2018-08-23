
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from taskhuddler.aio.graph import TaskGraph


async def async_main():
    """Run all the async tasks."""
    graph = await TaskGraph('b-ZKU1Q3QcKp3p7prOlURw')
    total_wall_time_buckets = defaultdict(timedelta)
    for task in graph.tasks():
        if task.completed:
            key = task.json['status']['workerType']
            total_wall_time_buckets[key] += task.resolved - task.started

    for bucket in total_wall_time_buckets:
        print("{}: {}".format(bucket, total_wall_time_buckets[kind]))

    # Extract cost per workertype from postgres

    # Do multiplications + sums


def main():
    """Manage the async loop."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
    loop.close()


if __name__ == '__main__':
    main()
