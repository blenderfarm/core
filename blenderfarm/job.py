
"""Job class."""

from . import serializable
from . import task

class Job(serializable.Serializable):

    """Describes a single job and remembers the status of each task within."""

    # ## Statuses

    # No tasks have been created for this job yet.
    STATUS_PENDING = 'pending'

    # At least one task has been sent off for completion.
    STATUS_WORKING = 'working'

    # Every task associated with this job has been fulfilled.
    STATUS_COMPLETE = 'complete'

    # One or more tasks on this job have failed.
    STATUS_FAILED = 'failed'

    # Currently in-progress tasks are saved, but further tasks are not
    # created.
    STATUS_PAUSED = 'paused'

    def __init__(self):
        self.status = Job.STATUS_PENDING

        # Contains a list of `Task`s.
        self.tasks = []

        # Contains a list of `task_id`s.
        self.working_tasks = []

    def unserialize(self, data):
        super().unserialize(data)

        self.tasks = []

        for task_serialized in data['tasks']:
            self.tasks.append(task.Task(self).unserialize(task_serialized))

        return self

    def serialize(self):
        out = super().serialize()

        out['tasks'] = []

        for task_object in self.tasks:
            out['tasks'].tasks.append(task_object.serialize())

        return out
