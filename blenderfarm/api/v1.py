
"""API v1."""

from .. import version
from . import api

class API(api.API):

    """Same name as `api.API`, but this is the v1 API implementation."""

    def __init__(self, server):
        super().__init__(server)
        
        self.api_version = '1'
        
    def init_routes(self):
        """Initialize routes."""

        self.route('__error_404', self.route_error_404)
        self.route('info.json', self.route_info)

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
    def route_info(request, response):
        """`info.json` route"""
        
        _ = request
        
        response.respond_json({
            'status': 'ok',
            'version': version.__version__
        })
        
