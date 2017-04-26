
"""Blenderfarm Server implementation."""

import json
import time
import traceback

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

from . import api
from . import db

class BlenderfarmHTTPServerRequestHandler(BaseHTTPRequestHandler):

    """Blenderfarm HTTP request handler. This has to manage the different
API versions and provide generic fallbacks in case the APIs mess
up. This class should always catch every exception."""

    def send_text(self, text_data):
        """This method encodes `text_data` as UTF-8, then responds with it."""

        self.wfile.write(bytes(text_data, 'utf8'))

    def send_json(self, json_data):
        """This method automatically converts the Python object into a JSON
string, then encodes it as UTF-8 and responds with it."""

        self.send_text(json.dumps(json_data))

    def respond_json(self, json_data, status=200):
        """Sets the HTTP status code and calls `send_json()`."""

        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.send_json(json_data)

        return

    def respond_error(self, status):
        """Responds with an HTTP error."""

        self.send_response(status)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        self.send_text(str(status))

        return

    def detect_api_version(self, path):
        """Given a path, tries to figure out which API endpoint to send it
to. Essentially, it splits the path into directories, then uses the
name of the first directory. For example, `/v1/foo.json` would result
in `['v1', 'foo.json']`. The second element will not start with a `/`,
but otherwise it should be identical to `path` minus the first
element."""

        # Remove the leading empty string in the resulting array.
        path = self.path.split('/')[1:]

        if len(path) >= 1:
            return [path[0], '/'.join(path[1:])]

        return [None, '/'.join(path)]

    # pylint: disable=invalid-name
    def do_method(self, method):
        """Responds to `method` requests."""

        try:

            api_version, path = self.detect_api_version(self.path)

            # Requesting `/`.
            if not api_version:
                print('No API version present in path "' + self.path + '"')
                self.respond_error(400)
                return

            # Requesting a path starting with something other than `v1`, `v2`, etc.
            if api_version not in self.api_handlers:
                print('No such API version "' + api_version + '" (path: "' + self.path + '")!')
                self.respond_error(400)
                return

            api_handler = self.api_handlers[api_version]

            # `API.get_route()` should *always* return a valid route; if
            # the requested route is missing, it should return its default
            # error handler route.
            route_handler = api_handler.get_route(method, path)

            # If the API handler has truly messed up, fall back to our
            # generic HTTP error response and respond with 500.
            if not route_handler:
                self.respond_error(500)
                return

            # `request, response`.
            route_handler(self, self)
            
        except Exception as _: # pylint: disable=broad-except
            print('Exception during "do_' + method + '":')
            traceback.print_exc()
            self.respond_error(500)

    # pylint: disable=invalid-name
    def do_GET(self):
        """Responds to `GET` requests."""

        self.do_method('GET')

    # pylint: disable=invalid-name
    def do_POST(self):
        """Responds to `POST` requests."""

        self.do_method('POST')

    def log_message(self, _format, *args):
        """Inhibit logging."""

        _ = _format, args
        
        return


#from . import api_v1

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class Server:

    """The server. Keeps track of jobs and clients."""

    def __init__(self, host='localhost', port=44363):

        # Server information.
        self.host = host
        self.port = port

        self.jobs = []

        self.init_api_handlers()
        self.init_server()

        self.users = db.Users()

        self.start_time = time.monotonic()

    def get_uptime(self):
        """Returns our uptime, in fractional seconds."""
        return time.monotonic() - self.start_time

    def init_api_handlers(self):
        """Initializes our API handlers."""
        
        self.api_handlers = {}

        v1 = api.v1.Server(self).init() # pylint: disable=invalid-name
        
        self.api_handlers['v1'] = v1

    def init_server(self):
        """Initialize the server."""

        request_handler = BlenderfarmHTTPServerRequestHandler
        request_handler.server = self

        request_handler.api_handlers = {
            'v1': self.api_handlers['v1']
        }

        self.httpd = ThreadedHTTPServer((self.host, self.port), request_handler)

        #self.api_v1 = api_v1.API(self).init()

    def start(self):
        """Starts the server."""

        self.httpd.serve_forever()

    def get_next_task(self, parameters):
        """Finds a new task that matches `parameters` as closely as possible."""
        pass
