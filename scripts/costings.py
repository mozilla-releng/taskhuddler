
import csv
import asyncio
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

import taskcluster.aio as taskcluster

from taskhuddler.aio.graph import TaskGraph


def fetch_worker_costs(year, month):
    """static snapshot of data from worker_type_monthly_costs table."""
    with open("july_raw_costs2.csv", 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        return {row[1]: float(row[4]) for row in reader}


def parse_args():
    parser = argparse.ArgumentParser(description="CI Costs")
    parser.add_argument('--taskgroupid', type=int)
    parser.add_argument('--revision', type=str)
    parser.add_argument('--nightly', action='store_true')
    parser.add_argument('--project', type=str, default='mozilla-central')
    parser.add_argument('--product', type=str, default='firefox')
    return parser.parse_args()


async def find_taskgroup_by_revision(args):

    if args.nightly:
        nightly_index = "nightly."
    else:
        nightly_index = ""
    index = "gecko.v2.{project}.{nightly}revision.{revision}.{product}.linux64-opt".format(
        project=args.project,
        nightly=nightly_index,
        revision=args.revision,
        product=args.product
    )
    print(index)
    idx = taskcluster.Index()
    queue = taskcluster.Queue()
    build_task = await idx.findTask(index)
    task_def = await queue.task(build_task['taskId'])

    return task_def['taskGroupId']


async def async_main():
    """Run all the async tasks."""
    args = parse_args()
    if args.taskgroupid:
        graph = await TaskGraph(args.taskgroupid)
    elif args.revision:
        graph_id = await find_taskgroup_by_revision(args)
        graph = await TaskGraph(graph_id)


    # graph = await TaskGraph('b-ZKU1Q3QcKp3p7prOlURw')
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
