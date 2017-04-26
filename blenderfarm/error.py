
"""Error class."""

class Error(Exception):

    """Contains a server error response (see [API.md](:../API.md))"""

    def __init__(self, code, message, context=None):
        super().__init__(message)
        
        self.code = code
        self.message = message
        self.context = context

        #print(code, message, context)

    def __str__(self):
        # pylint: disable=no-else-return
        
        if self.context:
            return self.message + ': "' + self.context + '"'
        elif self.message:
            return self.message
        else:
            return self.code
