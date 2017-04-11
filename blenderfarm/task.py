
"""Task."""

from . import serializable

class Task(serializable.Serializable):

    """A single task, executed by render nodes."""

    # ## Statuses

    def __init__(self, job):
        self.job = job

        # The `task_id` is unique to this `Job` and the task
        # itself. Each `Node` performing this `Task` will have the
        # same `task_id`; the only way to uniquely identify the output
        # of a single `Node` and `Task` combination is to use both
        # `node.node_id` and `task.task_id` at once.
        self.task_id = None

        # If `True`, this task will be ignored and never be completed.
        self.ignore = False

        # A list of nodes that are currently processing this task.
        self.nodes_working = []

    def should_execute(self):
        """Whether or not this task should be executed. This is run once per
render node. Returns `True` if it can be executed, `False`
otherwise."""

        if self.ignore:
            return False

    def unserialize(self, data):
        super().unserialize(data)

        self.ignore = data['ignore']

        return self

    def serialize(self):
        out = super().serialize()

        out['ignore'] = self.ignore

        return out
