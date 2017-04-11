
"""API handler."""

import sys

class API:

    """Primary class for API management."""

    def __init__(self, server):
        self.api_version = '0'

        self.server = server

        self.routes = {}

    def route(self, path, handler):
        """Adds a route to our list; binds `handler` to it. `handler` is a
function that accepts parameters `request, response` and does something."""
        self.routes[path] = handler

    def get_route(self, path):
        """Tries to find the appropriate route for `path`. Returns a generic
error handler if no route exists."""
        
        if path in self.routes:
            return self.routes[path]

        if '__error_404' in self.routes:
            return self.routes['__error_404']

        return None

    def init(self):
        """Called after `__init__()`. Returns `self` to allow for one-line
creation and initialization."""
        
        self.init_routes()

        # If there is no error route, bail out.
        if not self.get_route('__error_404'):
            print('error: subclasses of "API" should define an "__error_404" route')
            sys.exit(1)

        return self

    def init_routes(self):
        """Subclasses should override this method."""
        pass
