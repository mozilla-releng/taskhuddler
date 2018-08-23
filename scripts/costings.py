
import csv
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict

from taskhuddler.aio.graph import TaskGraph


def fetch_worker_costs(year, month):
    """static snapshot of data from worker_type_monthly_costs table."""
    with open("july_raw_costs2.csv", 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        return {row[1]: float(row[4]) for row in reader}


async def async_main():
    """Run all the async tasks."""
    graph = await TaskGraph('b-ZKU1Q3QcKp3p7prOlURw')
    total_wall_time_buckets = defaultdict(timedelta)
    for task in graph.tasks():
        if task.completed:
            key = task.json['status']['workerType']
            total_wall_time_buckets[key] += task.resolved - task.started

    for bucket in total_wall_time_buckets:
        print("{}: {}".format(bucket, total_wall_time_buckets[bucket]))

    year = graph.earliest_start_time.year
    month = graph.earliest_start_time.month
    worker_type_costs = fetch_worker_costs(year, month)

    total_cost = 0.0
    for bucket in total_wall_time_buckets:
        if bucket not in worker_type_costs:
            continue
        hours = total_wall_time_buckets[bucket].seconds/(60*60)
        cost = worker_type_costs[bucket] * hours
        print("{0}, {1}, ${2:.2f}".format(bucket, total_wall_time_buckets[bucket], cost))
        total_cost += cost


    print("Total cost: ${0:.2f}".format(total_cost))
    # Do multiplications + sums


def main():
    """Manage the async loop."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
    loop.close()


if __name__ == '__main__':
    main()
