#!/usr/bin/env python3

"""Blenderfarm server executable file."""

import blenderfarm.server

def start_server():
    """Starts the blenderfarm server."""
    
    server = blenderfarm.server.Server()
    server.start()

if __name__ == '__init__':
    start_server()
