
"""Blenderfarm server."""

class Server:

    """The server. Keeps track of jobs and clients."""

    def __init__(self):
        self.jobs = []

    def get_next_task(self, parameters):
        """Finds a new task that matches `parameters` as closely as possible."""
        pass
