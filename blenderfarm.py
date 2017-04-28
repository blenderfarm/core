#!/usr/bin/env python3

"""Blenderfarm server-side administrative tool."""

import blenderfarm.db
import sys

class Action:

    def __init__(self):
        self.name = None
        self.options = []

    def __lt__(self, other):
        return self.name < other.name

    def parse_arguments(self, args):
        options = {}

        for option_index in range(len(self.options)):
            option_format = self.get_option_format(self.options[option_index])

            option_name = option_format['name']
            option_value = option_format['default']

            if len(args) >= option_index + 1:
                option_value = args[option_index]
            elif option_format['optional'] == False:
                print('! option "' + option_name + '" (for action "' + self.name + '") is not optional')
                exit(1)

            options[option_name] = option_value

        if len(args) > len(self.options):
            options['__'] = args[len(self.options):]

        return options

    def get_option_help(self, option):
        """Converts an option format into its human-readable format."""

        option_format = self.get_option_format(option)
        name = option_format['name']

        if option_format['optional']:
            return '[' + name + ']'
        else:
            return name

    def get_option_format(self, option):
        """Converts an option format into a Python dictionary."""

        option_format = {
            'name': None,
            'optional': False,
            'default': None
        }

        # If the option is optional, set the `optional` flag.
        if option.startswith('?'):
            option = option[1:]
            option_format['optional'] = True

        # If there's a default value
        if '=' in option:
            option_format['default'] = option.split('=')[1]
            option = option.split('=')[0]

        option_format['name'] = option

        return option_format

    def get_string_options_list(self):
        options = []

        for option in self.options:
            options.append(self.get_option_help(option))

        return ' '.join(options)

    def get_help_line(self):
        return self.name.ljust(12) + ' ' + self.get_string_options_list().ljust(24) + ' ' + self.description

    def help(self, options):
        print(self.description)

    def invoke(self, options):
        print('override me')

class HelpAction(Action):

    def __init__(self):
        super().__init__()
        self.name = 'help'
        self.description = 'prints out help'
        self.options = ['?module']

    def invoke(self, options):
        
        print_version()

        print()

        # `help <foo>`
        if options['module'] != None:
            action_name = options['module']
            action = get_action(action_name)

            if not action:
                print_help()
                print()
                print('! no such action "' + action_name + '"')
                return

            print('help ' + action_name + ':')
            print()
            action.help(options)
        else:
            print_help()

class VersionAction(Action):

    def __init__(self):
        super().__init__()
        self.name = 'version'
        self.description = 'prints out the blenderfarm version'

    def help(self, options):
        print(self.description)
        print('only the version is printed, to make machine-parsing possible.')

    def invoke(self, options):
        print(blenderfarm.__version__)

class ServerAction(Action):

    def __init__(self):
        super().__init__()
        self.name = 'server'
        self.description = 'starts the blenderfarm server'
        self.options = ['?host=0.0.0.0', '?port=44363']

    def help(self, options):
        """Prints out help text for the `server` action."""
        
        print(self.description)

        print()

        print('accepts two arguments: [host] and [port].')
        print('If omitted, the defaults of "0.0.0.0" and "44363" are used.')

    def invoke(self, options):
        """Invokes the `server` action."""

        # Get `host` and `port` from the options.
        host = options['host']
        port = options['port']

        # Try converting the port to an int.
        try:
            port = int(port)
        except ValueError:
            print('! invalid port number "' + port + '"')
            return

        # Create the blenderfarm `Server`.
        server = blenderfarm.server.Server(host=host, port=port)

        # Print out a nice message, containing the host and port.
        print('starting blenderfarm server at ' + host + ' (' + str(port) + ')...')

        # And start the server.
        server.start()

# First, we define a list of actions.

ACTIONS = [
    HelpAction(),
    VersionAction(),
    
    ServerAction()
]

ACTIONS.sort()

def print_version():
    """Prints out the blenderfarm version in a human-readable format."""
    
    print('blenderfarm version ' + blenderfarm.__version__)

def print_help():
    """Prints out a list of actions, their options, and their descriptions in a human-readable format."""
    
    print('actions:')

    print()
    
    for action in ACTIONS:
        print(action.get_help_line())

def print_usage():
    """Prints out usage and help in a human-readable format."""
    
    print('usage: ' + sys.argv[0] + ' <action> [options...]')

    print()
    
    print_help()

def get_action(name):
    """Attempts to find the requisite action named `name`."""

    name = name.lower().strip()

    for action in ACTIONS:
        if action.name == name:
            return action

    return None

# Ideally, this would never be imported as a library, but just in case...
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print_usage()
        exit(1)

    action_name = sys.argv[1]
    action = get_action(action_name)

    if not action:
        print_usage()
        print()
        print('! no such action "' + action_name + '"')
        exit(1)

    action.invoke(action.parse_arguments(sys.argv[2:]))
