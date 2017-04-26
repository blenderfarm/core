
"""Blenderfarm client."""

from . import api

# # `Client`

class Client:

    """The main client class. It handles communicating with the server,
rendering the actual frames, and reporting progress back to the
server. It may optionally implement `Node`."""

    ## pylint: disable=too-many-instance-attributes,too-many-arguments
    
    def __init__(self, host='localhost', port=44363, username='anon', key='1234', insecure=False, is_node=False):

        self.api = api.v1.Client()

        # Server information.
        self.host = host
        self.port = port

        # If `True`, use `http` instead of `https`.
        self.insecure = insecure

        # Credentials.
        self.username = username
        self.key = key

        # Are we a node?
        self.is_node = is_node

        # The task we are currently performing. Only applicable if `is_node` is True.
        self.task = None

    # State utility functions.

    def is_connected(self):
        """Returns true if we have connected to the server. Because of
networking, we might not necessarily be able to connect, but we've
successfully authenticated already at some point."""
        
        return self.api.is_connected()

    def is_performing_task(self):
        """Returns `True` if we are currently performing a task."""
        return self.task != None

    # Getters.

    def get_task(self):
        """Returns the task we're working on, if present."""
        return self.task

    # Server info.

    def get_host_port(self):
        """Returns a human-readable "scheme://host:port/" string."""
        
        return self.api.get_host_port()

    def set_host_port(self, host, port):
        """Utility function to set host and port of the server. Returns `True`
if `host` and `port` have been set, `False` otherwise."""

        return self.api.set_host_port(host, port)

    def set_insecure(self, insecure):
        """Utility function to set HTTP/HTTPS. Returns `true` if the flag has been set, `False` otherwise."""

        return self.api.set_insecure(insecure)

    # Server connection utility functions.

    # ## Server connection

    def get_server_info(self, key):
        """Returns "key" of server info; for example, "version" or "uptime"."""
        return self.api.get_server_info(key)

    def connect(self, user, key):
        """Attempts to connect to the server. Does not catch any exceptions."""

        return self.api.connect(user, key)

    def disconnect(self):
        """Disconnects from the server."""

        return self.api.disconnect()
        
    # ## Lifecycle

    def idle(self):
        """Called whenever the client is idle."""

        pass

    def request_new_task(self):
        """Requests the next task from the server, and if it exists, performs it."""

        pass
