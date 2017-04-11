
"""Blenderfarm client."""

from urllib.parse import urljoin
import json

# Used for interfacing with the server. This is built into Blender so
# there aren't any problems when this is used as an addon.
import requests

# # `Error`

class Error(Exception):

    """Contains a server error response (see [API.md](:../API.md))"""

    def __init__(self, code, message, context=None):
        super().__init__(message)
        
        self.code = code
        self.message = message
        self.context = context

    def __str__(self):
        # pylint: disable=no-else-return
        
        if self.context:
            return self.message + ': "' + self.context + '"'
        elif self.message:
            return self.message
        else:
            return self.code


# # `Client`

class Client:

    """The main client class. It handles communicating with the server,
rendering the actual frames, and reporting progress back to the
server. It may optionally implement `Node`."""

    ## pylint: disable=too-many-instance-attributes,too-many-arguments
    
    def __init__(self, host='localhost', port=44363, username='anon', key='1234', insecure=False, is_node=False):

        # Server information.
        self.host = host
        self.port = port

        self.server_info = {
            'version': None
        }

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
        """Returns the task we're working on, if present."""
        return self.task

    # Server info setters.

    def set_host_port(self, host, port):
        """Utility function to set host and port of the server. Returns `True`
if `host` and `port` have been set, `False` otherwise."""

        if self.is_connected():
            return False
            
        self.host = host
        self.port = port

        return True

    def set_insecure(self, insecure):
        """Utility function to set HTTP/HTTPS. Returns `true` if the flag has been set, `False` otherwise."""

        if self.is_connected():
            return False
            
        self.insecure = insecure

        return True

    # Server connection utility functions.

    def get_host_port(self):
        """Returns a pretty `scheme://host:port` string."""

        return self.build_url()

    # ## Paths

    def build_url(self, path=''):
        """Builds a base URL for the server."""

        scheme = 'https'

        if self.insecure:
            scheme = 'http'

        return urljoin(scheme + '://' + self.host + ':' + str(self.port), path)

    
    # ## Parse response JSON

    @staticmethod
    def parse_json(json_string):
        """Parses a `json_string` and returns the Python object; raises
`Error('invalid-json')` if the string could not be decoded."""
        try:
            json_data = json.loads(json_string)
        except json.decoder.JSONDecodeError as _:
            print(json_string)
            
            raise Error('invalid-json', 'Invalid or malformed JSON could not be decoded')

        return json_data
    

    # ## Server communications

    def request_get(self, path):
        """Submits a `GET` request to the server."""
        
        try:
            response = self.session.get(self.build_url(path))
        except requests.exceptions.ConnectionError as _:
            print(_)
            raise Error('network-error', 'Could not connect to the server', self.get_host_port())

        # Handle the response.
        
        if response.status_code == 200:
            return self.parse_json(response.text)
        
        json_data = self.parse_json(response.text)

        if not all(k in json_data for k in ('status', 'code', 'message')):
            raise Error('invalid-json', 'Invalid or malformed JSON could not be decoded')
        
        raise Error(json_data['code'], json_data['message'], path)

    # ## Server connection

    def clear_server_info(self):
        """Resets server info."""
        
        self.server_info = {
            'version': None
        }


    def connect(self):
        """Attempts to connect to the server. Returns `True` if connection was
successful; `False` otherwise."""

        response = self.request_get('/v1/info.json')
        self.server_info['version'] = response['version']

        self.connected = True

        return True

    def disconnect(self):
        """Disconnects from the server."""

        self.connected = False

        self.clear_server_info()

        
    # ## Lifecycle

    def idle(self):
        """Called whenever the client is idle."""

        pass

    def request_new_task(self):
        """Requests the next task from the server, and if it exists, performs it."""

        pass
