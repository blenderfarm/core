
"""API v1."""

import json
import time

import requests

from .. import version as bf_version
from . import api as bf_api
from .. import error as bf_error
from .. import digest as bf_digest
from .. import task as bf_task
from .. import job as bf_job

class Server(bf_api.APIServer):

    """Same name as `api.API`, but this is the v1 API implementation."""

    def __init__(self, server):
        super().__init__(server)

        self.api_version = '1'

    def init_routes(self):
        """Initialize routes."""

        self.route('__', 'error_404', self.route_error_404)
        self.route('GET', '/info.json', self.route_info)
        
        self.route('GET', '/auth/test.json', self.route_auth_test)
        
        self.route('GET', '/job/get.json', self.route_job_get)
        
        self.route('GET', '/task/next.json', self.route_task_next)

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

        calculated_digest = bf_digest.get_key_value_digest(data, user.key)

        # Make sure the token matches.
        
        if not bf_digest.compare(data_digest, calculated_digest):
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
            'version': bf_version.__version__,
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

    def route_job_get(self, request, response):
        """Returns serialized info about a single `Job`."""

        if not self.verify_auth(request, response):
            return

        data = self.get_url_params(request, response)

        if not data:
            self.route_error_400(request, response)
            
            return False

        if 'job_id' not in data:
            print('missing URL parameter "job_id"')
            self.route_error_400(request, response, context='missing parameters')
            
            return False

        job_id = data['job_id']
        
        job = self.server.jobs.get_job(job_id)

        if not job:
            response.respond_json({
                'status': 'error',
                'code': 'invalid-job',
                'message': 'No such job',
                'context': job_id
            })
            return
        
        response.respond_json({
            'status': 'ok',
            'job': job.serialize(net=True)
        })

    def route_task_next(self, request, response):
        """Next task route."""

        if not self.verify_auth(request, response):
            return

        job = self.server.jobs.get_next_job()

        if not job:
            response.respond_json({
                'status': 'ok',
                'task': None
            })
            return

        task = job.get_next_task()
        
        response.respond_json({
            'status': 'ok',
            'task': task.serialize()
        })


class Client(bf_api.APIClient):

    """v1 API client (must talk with the v1 server, above)"""

    def __init__(self):
        super().__init__()

        self.server_info = {}

        self.clear_local_state()

        self.api_version = '1'

        self.user = None
        self.key = None

        self.jobs = {}
        self.task = []

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

            raise bf_error.Error('invalid-json', 'Invalid or malformed JSON could not be decoded')

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

        if not isinstance(json_data, dict) or response.status_code != 200:
            raise bf_error.Error('http-error', 'Server returned an error status', context=str(response.status_code))
        
        if json_data['status'] == 'ok' or not raise_errors:
            return json_data

        if not all(k in json_data for k in ('code', 'message')):
            raise bf_error.Error('invalid-json', 'Invalid or malformed JSON could not be decoded')

        context = path

        if 'context' in json_data:
            context = json_data['context']
            
        raise bf_error.Error(json_data['code'], json_data['message'], context)

    # ## Low-level communications

    def request_get(self, path, params=None, raise_errors=False, auth=False):
        """Submits a `GET` request to the server. The path must *not* start with a leading '/'."""

        if not params:
            params = {}

        if auth:
            params = self.add_auth(params)

        try:
            response = self.session.get(self.build_url(path), params=params)
        except requests.exceptions.ConnectionError as _:
            raise bf_error.Error('network-error', 'Could not connect to the server', self.get_host_port())

        return self.handle_response(path, response, raise_errors)

    def request_post(self, path, params=None, data=None, raise_errors=False, auth=False):
        """Submits a `POST` request to the server. The path must *not* start with a leading '/'."""

        if not params:
            params = {}

        if auth:
            params = self.add_auth(params)

        try:
            response = self.session.post(self.build_url(path), params=params, data=data)
        except requests.exceptions.ConnectionError as _:
            raise bf_error.Error('network-error', 'Could not connect to the server', self.get_host_port())

        return self.handle_response(path, response, raise_errors)

    def add_auth(self, data):
        """Injects the HMAC digest into URL parameter data."""
        
        data['user'] = self.user
        data['time'] = str(0)

        data['digest'] = bf_digest.get_key_value_digest(data, self.key)

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
        
        response = self.request_get('/auth/test.json', auth=True, raise_errors=True)

        # If any errors happened above, they would have raised an exception, so we're good here.

    def request_next_task(self):
        """Requests the next task task from the server."""
        
        response = self.request_get('/task/next.json', auth=True, raise_errors=True)

        if not response['task']:
            return None

        next_task = bf_task.Task(None).unserialize(response['task'])

        job_id = next_task.job_id

        if job_id not in self.jobs:
            job = self.request_job(job_id)

            self.jobs[job_id] = job

        return bf_task.Task(self.jobs[job_id]).unserialize(response['task'])
        
    def download_job_file(self, job, filename):
        """Submits a `GET` request to the server. The path must *not* start with a leading '/'."""

        url = job.job_info.file_url

        try:
            with open(filename, 'wb') as handle:
                
                response = self.session.get(url, stream=True)

                if not response.ok:
                    raise bf_error.Error('network-error', 'Could not download file for job', url)

                for block in response.iter_content(1024):
                    handle.write(block)
        except requests.exceptions.ConnectionError as _:
            raise bf_error.Error('network-error', 'Could not download file for job', url)

        return filename
        
    def request_job(self, job_id):
        """Gets the job information for `job_id`."""

        response = self.request_get('/job/get.json', params={'job_id': job_id}, auth=True, raise_errors=True)

        return bf_job.Job(None).unserialize(response['job'])

    # ## High-level connect/disconnect

    def connect(self, user, key):
        """Connects to the server. Raises an [`Error`](:../error.py) if connection is unsuccessful."""

        self.user = user
        self.key = key

        try:
            self.request_server_info()
            self.request_auth_test()
        except bf_error.Error as exception:
            self.clear_local_state()
            
            raise exception # pylint: disable=raising-bad-type

        self.connection_start_time = time.monotonic()

        self.connected = True

    def disconnect(self):
        """Disconnects from the server."""
        
        self.clear_local_state()

        self.connected = False
