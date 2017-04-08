
"""Blenderfarm client."""

from urllib.parse import urljoin

# Used for interfacing with the server.
import requests

class Client:

    """The main client class. It handles communicating with the server,
rendering the actual frames, and reporting progress back to the
server. It may optionally implement `Node`."""

    # pylint: disable=too-many-instance-attributes,too-many-arguments

    def __init__(self, hostname='localhost', port=44363, username='anon', key='1234', insecure=False, is_node=False):

        # Server information.
        self.hostname = hostname
        self.port = port

        # Credentials.
        self.username = username
        self.key = key

        # If `True`, use `http` instead of `https`.
        self.insecure = insecure

        # Are we a node?
        self.is_node = is_node

        # ## Dynamic state

        self.connected = False

        # The task we are currently performing. Only applicable if `is_node` is True.
        self.task = None

        self.session = requests.Session()

    # State utility functions.

    def is_connected(self):
        """Returns true if we have connected to the server. Because of
networking, we might not necessarily be able to connect, but we've
successfully authenticated already at some point."""
        return self.connected

    def is_performing_task(self):
        """Returns `True` if we are currently performing a task."""
        return self.task != None

    # Getters.

    def get_task(self):
        return self.task

    # Server connection utility functions.

    def get_hostname_port(self):
        """Returns a pretty `hostname:port` string."""

        return self.get_url()

    def get_url(self, path=''):
        """Builds a base URL for the server."""

        scheme = 'https'

        if self.insecure:
            scheme = 'http'

        return urljoin(scheme + '://' + self.hostname + ':' + str(self.port), path)

    # ## Server connection

    def connect(self):
        """Attempts to connect to the server."""

        try:
            response = self.session.get(self.get_url('/version'))
        except requests.exceptions.ConnectionError as _:
            return False

        print(response.status_code)

        self.connected = True

        return True

    def disconnect(self):
        """Disconnects from the server."""

        self.connected = False

    # ## Lifecycle

    def idle(self):
        """Called whenever the client is idle."""

        pass

    def request_new_task(self):
        """Requests the next task from the server, and if it exists, performs it."""

        pass
