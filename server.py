#!/usr/bin/env python3

"""Blenderfarm server executable file."""

import blenderfarm.server

def start_server():
    """Starts the blenderfarm server."""

    # Print out the version.
    print('blenderfarm v' + blenderfarm.__version__)

    # Create the server; we bind to `0.0.0.0` instead of `localhost`
    # to allow external hosts to connect.
    server = blenderfarm.server.Server(host='0.0.0.0', port=44363)

    # And start the server!
    print('starting blenderfarm server...')
    server.start()

# Ideally, this would never be imported as a library, but just in case...
if __name__ == '__main__':
    start_server()
