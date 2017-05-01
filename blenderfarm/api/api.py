
"""API handler."""

import sys
import urllib.parse

# Used for interfacing with the server. This is built into Blender so
# there aren't any problems when this is used as an addon.
import requests

class APIServer:

    """Primary class for API management."""

    def __init__(self, server):
        self.api_version = '0'

        self.server = server

        self.routes = {}

    def route(self, method, path, handler):
        """Adds a route to our list; binds `handler` to it. `handler` is a
function that accepts parameters `request, response` and does something."""

        if method not in self.routes:
            self.routes[method] = {}

        self.routes[method][path] = handler

    def get_route(self, method, path=None):
        """Tries to find the appropriate route for `path`. Returns a generic
error handler if no route exists."""

        if not path:
            path = method
            method = 'GET'

        path = '/' + urllib.parse.urlparse(path).path
        
        if method in self.routes:
            if path in self.routes[method]:
                print(method + ': ' + path)
                return self.routes[method][path]

        if 'error_404' in self.routes['__']:
            print('__: error_404 (requested: ' + method + ': ' + path + ')')
            return self.routes['__']['error_404']

        return None

    def init(self):
        """Called after `__init__()`. Returns `self` to allow for one-line
creation and initialization."""

        self.init_routes()

        # If there is no error route, bail out.
        if '__' not in self.routes or 'error_404' not in self.routes['__']:
            print('error: subclasses of "API" should define an "error_404" route with the "__" method')
            sys.exit(1)

        return self

    def init_routes(self):
        """Subclasses should override this method."""
        pass

    @staticmethod
    def get_url_params(request, response):
        """Returns the URL parameters; `{}` if none present."""

        _ = response
        
        data = urllib.parse.parse_qs(urllib.parse.urlparse(request.path).query)

        return {x: data[x][0] for x in data}

    @staticmethod
    def get_post_data(request, response):
        """Returns the `POST` data; `{}` if none present."""

        _ = response
        
        content_length = request.headers.get('content-length')

        if not content_length:
            return {}
        
        length = int(content_length)
        data = str(request.rfile.read(length), 'utf8')
        data = urllib.parse.parse_qs(urllib.parse.urlparse('?' + data).query)

        return {x: data[x][0] for x in data}

    
class APIClient:
    """Manages connecting to an API server."""

    def __init__(self, host='localhost', port=44363, insecure=False):
        self.api_version = '0'

        # Server information.
        self.host = host
        self.port = port

        # If `True`, use `http` instead of `https`.
        self.insecure = insecure

        self.session = requests.Session()

        # ## Dynamic state

        self.connected = False

    def get_host_port(self):
        """Returns a human-readable "scheme://host:port/" string."""

        return self.build_url(api_version=False)

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

    def is_connected(self):
        """Returns true if we have connected to the server. Because of
networking, we might not necessarily be able to connect, but we've
successfully authenticated already at some point."""

        return self.connected

    # ## Paths

    def build_url(self, path='', api_version=True):
        """Builds a base URL for the server."""

        scheme = 'https'

        if self.insecure:
            scheme = 'http'

        if api_version:
            path = '/v' + self.api_version + path

        return urllib.parse.urljoin(scheme + '://' + self.host + ':' + str(self.port), path)
