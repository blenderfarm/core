
"""Job class."""

from . import db
from . import serializable
from . import task

class JobInfo(serializable.Serializable):

    """Contains data about a particular job."""

    def __init__(self, job):
        self.job = job

    def get_info_type(self):
        return 'none'

    def unserialize(self, data):
        return self

    def serialize(self):
        return {}
    
    
class JobInfoRender(JobInfo):

    """`JobInfo` containing render information"""

    def __init__(self, job):
        super().__init__(job)

        self.file_url = ''

        self.resolution = [1920, 1080]

        # Renders frames from `[0]` to `[1]-1`.
        self.frame_range = [0, 1]

    def get_info_type(self):
        return 'render'

    def unserialize(self, data):
        super().unserialize(data)

        self.file_url = data['file_url']
        self.frame_range = data['frame_range']
        self.resolution = data['resolution']

        return self

    def get_tasks(self):

        tasks = []

        for frame in range(self.frame_range[0], self.frame_range[1]):
            frame_task = task.Task(self.job)
            
            task_info = task.TaskInfoRender(frame_task)
            task_info.frame = frame

            frame_task.task_info = task_info
            
            tasks.append(frame_task)

        return tasks
            
    def serialize(self):
        out = super().serialize()

        out['file_url'] = self.file_url
        out['frame_range'] = self.frame_range
        out['resolution'] = self.resolution

        return out

    
# Job

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

    def __init__(self, job_info):
        self.status = Job.STATUS_PENDING

        self.job_id = db.generate_uuid()

        self.job_info = job_info

        # Contains a list of `Task`s.
        self.tasks = []

        # Contains a list of `task_id`s.
        self.working_tasks = []

        if job_info:
            self.job_info.job = self

    def populate_tasks(self):
        self.tasks = self.job_info.get_tasks()
        
    def get_task(self, task_id):
        """Returns the task with `task_id`, or `None` if no such task exists."""

        print(self.tasks, task_id)
        
        for task in self.tasks:
            if task.task_id == task_id:
                return task

        return None

    def unserialize(self, data):
        self.job_id = data['job_id']

        job_info_type = data['job_info_type']
        
        if job_info_type == 'render':
            self.job_info = JobInfoRender(self)
        else:
            print("oh god we don't know what to do with a 'JobInfo' of type '" + job_info_type + "'; things will break")
            return
            
        self.job_info.unserialize(data['job_info'])

        if 'tasks' in data:
            self.tasks = []

            for task_serialized in data['tasks']:
                self.tasks.append(task.Task(self).unserialize(task_serialized))

        return self

    def serialize(self, net=False):
        out = {}

        out['job_id'] = self.job_id

        out['job_info_type'] = self.job_info.get_info_type()
        out['job_info'] = self.job_info.serialize()

        if not net:
            out['tasks'] = []

            for task_object in self.tasks:
                out['tasks'].append(task_object.serialize())

        return out

    def get_job_line(self):
        """Returns a human-readable job info string."""
        return self.job_id.ljust(24)

    def get_next_task(self):
        """Returns the highest-priority task."""

        if not self.tasks:
            return None

        for task in self.tasks:
            if task.should_execute():
                return task

        return None

    
# # JobsList
    
class JobList(db.DB):
    """Jobs database."""

    def __init__(self):
        super().__init__('jobs.json')

        self.jobs = []

        # If we don't have any saved data, save the DB.
        if not self.restore():
            self.save()

    # # Save/restore

    def _save(self):
        out_jobs = []

        for job in self.jobs:
            out_jobs.append(job.serialize())

        return out_jobs

    def _restore(self, data):
        self.jobs = []

        for job_data in data:
            job = Job(None)
            job.unserialize(job_data)

            self.jobs.append(job)

    def add(self, job):
        """Adds a job."""

        self.refresh()

        self.jobs.append(job)

        self.save()

        return True

    def get_jobs(self):
        return self.jobs

    def get_job(self, job_id):
        """Returns the job with `job_id`, or `None` if no such job exists."""
        
        for job in self.jobs:
            if job.job_id == job_id:
                return job

        return None

    def get_next_job(self):
        """Returns the highest-priority job."""
        
        if not self.jobs:
            return None

        # Obviously, this is a temporary placeholder.
        return self.jobs[0] # TODO duh.
