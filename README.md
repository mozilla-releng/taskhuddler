
A higher level wrapper around [taskcluster-client.py](https://github.com/taskcluster/taskcluster-client.py) with the aim of having a more Pythonic interface to taskcluster.

Currently aiming to get easier, read-only features available.

## Usage

```python
from taskhuddler import TaskGraph

# All queries here will result in API calls
graph = TaskGraph('M5hSue6oRSu_klunMRHolg') 
for task in graph.tasks():
    print(task['status']['taskId'])

# All tasks will be cached locally when TaskGraph is called
# But this means data may get stale.
cached_graph = TaskGraph('M5hSue6oRSu_klunMRHolg', caching=True) 
for task in cached_graph.tasks():
    print(task['status']['taskId'])
cached_graph.refresh_task_cache()

# Are all the tasks in the 'completed' state?
print(cached_graph.completed)

```

## Plans

* Let TaskGraph be used as a context manager
* Reduce the per-query limit for cached graphs so the initial response is quicker
* Make better use of Task classes for extra checks.
* Allow filters for task lists, so that things like this work: `graph.tasks(filter=lambda name: task['metadata']['name'] == name)
