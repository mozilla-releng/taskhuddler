"""
Analyze timing information in nightly task graphs.
"""

import asyncio
from datetime import datetime, timedelta

from taskhuddler.aio.nightly import find_nightly_graphs
import pandas as pd


async def async_main():
    """Run all the async tasks."""
    end = datetime.now()
    start = datetime.now() - timedelta(100)
    graphs = await find_nightly_graphs(start=start, end=end)

    results = list()
    for date in graphs:
        print("{} {}".format(date, graphs[date]))
        for t in graphs[date].task_timings():
            t.update({'date': date})
            results.append(t)

    df = pd.DataFrame(results)

    summary = df.groupby(['date', 'kind', 'platform'], as_index=False).agg({'duration': ['min', 'max', 'mean', 'count']})
    summary.columns = ["_".join(x).rstrip('_') for x in summary.columns.ravel()]

    summary.to_csv('output.csv')


def main():
    """Manage the async loop."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
    loop.close()


if __name__ == '__main__':
    main()
