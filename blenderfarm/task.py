
"""Task."""

from . import db
from . import serializable

class TaskInfo(serializable.Serializable):

    """Contains data about a particular task."""

    def __init__(self, task):
        self.task = task

    def get_info_type(self):
        return "none"

    
class TaskInfoRender(TaskInfo):

    """`TaskInfo` containing render information"""

    def __init__(self, task):
        super().__init__(task)
        
        self.resolution = [1920, 1080]

    def get_info_type(self):
        return "render"

    def unserialize(self, data):
        super().unserialize(data)

        self.resolution = data['resolution']

        return self

    def serialize(self):
        out = super().serialize()

        out['resolution'] = self.resolution

        return out

    
class Task(serializable.Serializable):

    """A single task, executed by render nodes."""

    # ## Statuses

    def __init__(self, job):
        # While `job` is a required argument, it might be `None` sometimes.
        
        self.job = job

        self.job_id = None

        if job:
            self.job_id = job.job_id

        # The `task_id` is unique to this `Job` and the task
        # itself. Each `Node` performing this `Task` will have the
        # same `task_id`; the only way to uniquely identify the output
        # of a single `Node` and `Task` combination is to use both
        # `node.node_id` and `task.task_id` at once.
        self.task_id = db.generate_uuid()

        # If `True`, this task will be ignored and never be completed.
        self.ignore = False

        self.complete = False

        self.task_info = TaskInfoRender(self)

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

        self.job_id = data['job_id']

        self.task_id = data['task_id']
        self.ignore = data['ignore']

        task_info_type = data['task_info_type']
        
        if task_info_type == 'render':
            self.task_info = TaskInfoRender(self)
        else:
            print("oh god we don't know what to do with a 'TaskInfo' of type '" + task_info_type + "'; things will break")
            return
            
        self.task_info.unserialize(data['task_info'])

        return self

    def serialize(self):
        out = super().serialize()

        out['job_id'] = self.job.job_id
        
        out['task_id'] = self.task_id
        out['ignore'] = self.ignore
        
        out['task_info_type'] = self.task_info.get_info_type()
        out['task_info'] = self.task_info.serialize()

        return out
