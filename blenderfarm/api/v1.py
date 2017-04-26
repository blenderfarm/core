
"""API v1."""

import json
import time

import requests

from .. import version
from . import api
from .. import error
from .. import digest

class Server(api.APIServer):

    """Same name as `api.API`, but this is the v1 API implementation."""

    def __init__(self, server):
        super().__init__(server)

        self.api_version = '1'

    def init_routes(self):
        """Initialize routes."""

        self.route('__', 'error_404', self.route_error_404)
        self.route('GET', 'info.json', self.route_info)
        
        self.route('GET', 'auth/test.json', self.route_auth_test)

    @staticmethod
    def route_error_404(request, response):
        """404 error route."""

        _ = request

        response.respond_json({
            'status': 'error',
            'code': '404',
            'message': '404 Not Found'
        }, status=404)

    @staticmethod
    def route_error_400(request, response, message='400 Bad Request', context=''):
        """400 error route."""

        _ = request

        response.respond_json({
            'status': 'error',
            'code': '400',
            'message': message,
            'context': context
        }, status=400)

    def verify_auth(self, request, response):
        """Verifies that the user is authenticated."""
        
        data = self.get_url_params(request, response)

        if not data:
            self.route_error_400(request, response)
            
            return False

        if not all(k in data for k in ('user', 'time', 'digest')):
            self.route_error_400(request, response, context='missing parameters')
            
            return False

        # Store the digest and remove it from the data dictionary.

        data_user = data['user']

        # Make sure that user exists.
        user = self.server.users.get_user(data_user)

        if not user:
            response.respond_json({
                'status': 'error',
                'code': 'invalid-user',
                'message': 'No such user',
                'context': data_user
            })
            
            return
        
        data_digest = data['digest']
        del data['digest']

        calculated_digest = digest.get_key_value_digest(data, user.key)

        # Make sure the token matches.
        
        if not digest.compare(data_digest, calculated_digest):
            response.respond_json({
                'status': 'error',
                'code': 'invalid-key',
                'message': 'Missing or incorrect authentication key',
                'context': data_user
            })
            
            return

        return True
        
    def route_info(self, request, response):
        """`info.json` route"""

        _ = request

        response.respond_json({
            'status': 'ok',
            'version': version.__version__,
            'uptime': self.server.get_uptime(),
            'time': time.time()
        })

    def route_auth_test(self, request, response):
        """Authentication test route."""

        if not self.verify_auth(request, response):
            return

        response.respond_json({
            'status': 'ok'
        })


class Client(api.APIClient):

    """v1 API client (must talk with the v1 server, above)"""

    def __init__(self):
        super().__init__()

        self.server_info = {}

        self.clear_local_state()

        self.api_version = '1'

        self.user = None
        self.key = None

        self.connection_start_time = 0

    def clear_server_info(self):
        """Resets server info. Called when disconnecting (so we don't show
stale server info.)"""
        
        self.server_info = {
            'version': None,
            'uptime': None
        }

    def clear_local_state(self):
        """Clears local state. Used in case of aborted connections or when
disconnecting."""
        self.clear_server_info()

        self.user = None
        self.key = None

    # ## Parse response JSON

    @staticmethod
    def parse_json(json_string):
        """Parses a `json_string` and returns the Python object; raises
`error.Error('invalid-json')` if the string could not be decoded."""
        
        try:
            json_data = json.loads(json_string)
        except json.decoder.JSONDecodeError as _:
            print('Could not decode JSON:')
            print(json_string)

            raise error.Error('invalid-json', 'Invalid or malformed JSON could not be decoded')

        return json_data

    def get_server_info(self, key):
        """Returns "key" of server info; for example, "version" or "uptime"."""

        if key == 'version':
            return self.server_info['version']
        
        # Values that increment with time.
        elif key == 'uptime' or key == 'time':
            if self.server_info[key]:
                return self.server_info[key] + time.monotonic() - self.connection_start_time
            return None


    def handle_response(self, path, response, raise_errors=False):
        """Handles a response from the server. If `raise_errors` is True,
then any errors will be raised directly instead of being returned as a
Python object."""
        
        # Handle the response.

        json_data = self.parse_json(response.text)

        print('Response: ' + response.text)

        if not isinstance(json_data, dict) or response.status_code != 200:
            raise error.Error('http-error', 'Server returned an error status', context=str(response.status_code))
        
        if json_data['status'] == 'ok' or not raise_errors:
            return json_data

        if not all(k in json_data for k in ('code', 'message')):
            raise error.Error('invalid-json', 'Invalid or malformed JSON could not be decoded')

        context = path

        if 'context' in json_data:
            context = json_data['context']
            
        raise error.Error(json_data['code'], json_data['message'], context)

    # ## Low-level communications

    def request_get(self, path, params=None, raise_errors=False):
        """Submits a `GET` request to the server. The path must *not* start with a leading '/'."""

        try:
            response = self.session.get(self.build_url(path), params=params)
        except requests.exceptions.ConnectionError as _:
            raise error.Error('network-error', 'Could not connect to the server', self.get_host_port())

        return self.handle_response(path, response, raise_errors)

    def request_post(self, path, params=None, data=None, raise_errors=False):
        """Submits a `POST` request to the server. The path must *not* start with a leading '/'."""

        try:
            response = self.session.post(self.build_url(path), params=params, data=data)
        except requests.exceptions.ConnectionError as _:
            raise error.Error('network-error', 'Could not connect to the server', self.get_host_port())

        return self.handle_response(path, response, raise_errors)

    def add_auth(self, data):
        """Injects the HMAC digest into URL parameter data."""
        
        data['user'] = self.user
        data['time'] = self.user

        data['digest'] = digest.get_key_value_digest(data, self.key)

        return data

    # ## Actual server communications
    
    def request_server_info(self):
        """Requests server info from server and populates our `server_info` fields."""
        
        response = self.request_get('/info.json')

        self.server_info['version'] = response['version']
        self.server_info['uptime'] = response['uptime']
        self.server_info['time'] = response['time']

    def request_auth_test(self):
        """Makes sure the user/key pair is valid."""
        
        response = self.request_get('/auth/test.json', params=self.add_auth({}), raise_errors=True)

        print(json.dumps(response))

    # ## High-level connect/disconnect

    def connect(self, user, key):
        """Connects to the server. Raises an [`Error`](:../error.py) if connection is unsuccessful."""

        self.user = user
        self.key = key

        try:
            self.request_server_info()
            self.request_auth_test()
        except error.Error as exception:
            self.clear_local_state()
            
            raise exception # pylint: disable=raising-bad-type

        self.connection_start_time = time.monotonic()

        self.connected = True

    def disconnect(self):
        """Disconnects from the server."""
        
        self.clear_local_state()

        self.connected = False
