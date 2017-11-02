

class Task(object):
    """docstring for Task."""

    def __init__(self, json=None):
        self.definition = json

    # Properties to extract commonly used values.

    @property
    def taskid(self):
        return self.definition['status']['taskId']

    @property
    def state(self):
        return self.definition['status'].get('state', '')

    @property
    def completed(self):
        """Has this task completed.

        Returns: Bool
            if the highest runId has state 'completed'
        """
        return self.state == 'completed'
