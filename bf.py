#!/usr/bin/env python3

"""Blenderfarm command-line tool."""

import sys

import blenderfarm

class Action:
    """A command-line action that can be executed."""

    def __init__(self):
        self.name = ''
        self.description = ''

        # Options format: `?name=default`
        #
        # The question mark denotes an optional argument, the name is
        # a plain string, and the optional default is an equals sign,
        # followed by the default string value.
        
        self.options = []

        # Used internally to display nicely formatted command-line text.
        self.prefix = ''

    def __lt__(self, other):
        """Make sorting work."""
        
        return self.name < other.name

    def parse_arguments(self, args, raise_errors=False):
        """Inserts actual arguments into `options` array that contains the
named options (see `self.options`, above)."""
        
        options = {}

        # For each option in our list of valid options;
        for option_index in range(len(self.options)):

            # convert it into a dictionary containing `name`,
            # `optional`, and `default.
            option_format = Action.get_option_format(self.options[option_index])

            # Just to make it a bit easier.
            option_name = option_format['name']
            option_value = option_format['default']

            # If the argument exists in `args`, then save the value.
            if len(args) >= option_index + 1:
                option_value = args[option_index]
            # Otherwise, if the option is not optional and also not
            # present, and _also_ we've asked to raise errors (for
            # example, the help dialogs don't want to raise errors),
            # then complain and exit.
            elif not option_format['optional'] and raise_errors:
                print('! option "' + option_name + '" (for action "' + self.name + '") is not optional')
                exit(1)

            # Set the value of the option dictionary.
            options[option_name] = option_value

        # Take all extra arguments and stuff them into `__`.
        if len(args) > len(self.options):
            options['__'] = args[len(self.options):]
        else:
            options['__'] = []

        return options

    @staticmethod
    def get_option_help(option):
        """Converts an option format into its human-readable format."""

        option_format = Action.get_option_format(option)
        name = option_format['name']

        # Optional arguments are surrounded with `[square brackets]`.
        if option_format['optional']:
            return '[' + name + ']'
        
        # Required arguments are surrounded with `<angle brackets>`.
        return '<' + name + '>'

    @staticmethod
    def get_option_format(option):
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
        """Get a human-readable list of all the options. Used in help and usage."""
        options = []

        for option in self.options:
            options.append(Action.get_option_help(option))

        return ' '.join(options)

    def get_help_line(self):
        """Returns a human-readable help line, containing the prefix, the name, options, and the description."""
        
        return self.prefix + ' ' + self.name.ljust(12) + ' ' + self.get_string_options_list().ljust(24) + ' ' + self.description

    def get_help_usage(self):
        """Same as above, but formatted slightly differently for usage listings."""

        return (self.prefix + ' ' + self.name + ' ' + self.get_string_options_list()).ljust(48) + self.description

    def help(self, options):
        """Prints out the help for this action."""

        _ = options
        
        print(self.get_help_usage())

    def invoke(self, options):    # pylint: disable=no-self-use
        """Invokes this action."""
        
        _ = options
        
        print('override me')

class ActionList(Action):
    """An action that contains sub-actions."""

    def __init__(self):
        super().__init__()
        self.options = ['action']

        self.actions = []

    def get_action(self, name):
        """Attempts to find the requisite sub-action named `name`."""

        name = name.lower().strip()

        for action in self.actions:
            if action.name == name:
                return action

        return None

    def help(self, options):
        """Prints out help text, including help text for sub-actions."""

        action_name = options['action']

        if action_name:
            action = self.get_action(action_name)

            if action:
                action.prefix = self.prefix + ' ' + self.name

                action.help(action.parse_arguments(options['__']))

                return

        print(self.get_help_usage())

        print()

        for action in self.actions:
            action.prefix = self.prefix + ' ' + self.name
            print(action.get_help_usage())

    def invoke(self, options):
        """Invokes the action."""

        # Get action name and arguments (will be an empty array if none are present.)
        action_name = options['action']
        arguments = options['__']

        action = self.get_action(action_name)

        if not action:
            self.help(options)
            print()
            print('! no such sub-action "' + action_name + '"')
            return

        action.prefix = self.prefix + ' ' + self.name
        action.invoke(action.parse_arguments(arguments, True))


class HelpAction(Action):
    """Prints out the help page."""

    def __init__(self):
        super().__init__()
        self.name = 'help'
        self.description = 'prints out help'
        self.options = ['?module']

    def invoke(self, options):
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

            action.prefix = self.prefix
            action.help(action.parse_arguments(options['__']))
        else:
            print_help()

        print()

class VersionAction(Action):
    """Prints out the blenderfarm version."""

    def __init__(self):
        super().__init__()
        self.name = 'version'
        self.description = 'prints out the blenderfarm version'

    def help(self, options):
        print(self.get_help_usage())

        print()

        print('only the version is printed, to make machine-parsing possible.')

    def invoke(self, options):
        print(blenderfarm.__version__)

class ServerAction(Action):
    """Starts the blenderfarm server."""

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

class AdminUserAddAction(Action):
    """Adds a blenderfarm user."""

    def __init__(self):
        super().__init__()
        self.name = 'add'
        self.description = 'adds a new user'
        self.options = ['username']

    def help(self, options):
        print(self.description)
        print()
        print('the username must not exist yet')

    def invoke(self, options):
        """Invokes the `user add` action."""

        username = options['username']

        users_db = blenderfarm.db.Users()

        user = users_db.get_user(username)

        if user:
            print('that username already exists:')
        else:
            user = users_db.add(username)
            print('user creation successful:')

        print(user.get_username_key())


class AdminUserRemoveAction(Action):
    """Removes a blenderfarm user."""

    def __init__(self):
        super().__init__()
        self.name = 'remove'
        self.description = 'removes a user'
        self.options = ['username']

    def invoke(self, options):
        """Invokes the `user remove` action."""

        username = options['username']

        users_db = blenderfarm.db.Users()

        if not users_db.get_user(username):
            print('! that username does not exist')
            return

        users_db.remove(username)

        print('user deletion successful; "' + username + '" no longer exists')


class AdminUserRekeyAction(Action):
    """Changes a blenderfarm user's key."""

    def __init__(self):
        super().__init__()
        self.name = 'rekey'
        self.description = 'deletes the old user key and creates a new one'
        self.options = ['username']

    def invoke(self, options):
        """Invokes the `user rekey` action."""

        username = options['username']

        users_db = blenderfarm.db.Users()

        user = users_db.get_user(username)

        if not user:
            print('! that username does not exist')
            return

        users_db.rekey(username)

        print('user rekey successful')
        print(user.get_username_key())


class AdminUserListAction(Action):
    """List all blenderfarm users."""

    def __init__(self):
        super().__init__()
        self.name = 'list'
        self.description = 'lists users and keys'
        self.options = ['?username']

    def help(self, options):
        print(self.get_help_usage())
        print()
        print('lists existing users on this blenderfarm server')
        print('if the optional parameter [username] is present, only lists that user')

    def invoke(self, options):
        """Invokes the `user list` action."""

        users_db = blenderfarm.db.Users()

        username = options['username']

        if username:
            user = users_db.get_user(username)

            if user:
                print('...')
                print(user.get_username_key())
                print('...')
                return

            print('! that username does not exist')
            return

        for user in users_db.get_users():
            print(user.get_username_key())


class AdminUserAction(ActionList):
    """`ActionList` for user actions."""

    def __init__(self):
        super().__init__()
        self.name = 'user'
        self.description = 'blenderfarm server user administration commands'

        self.actions = [
            AdminUserAddAction(),
            AdminUserRemoveAction(),
            AdminUserRekeyAction(),
            AdminUserListAction()
        ]

class AdminAction(ActionList):
    """`ActionList` for admin actions."""

    def __init__(self):
        super().__init__()
        self.name = 'admin'
        self.description = 'blenderfarm server administration commands'

        self.actions = [
            AdminUserAction()
        ]

# First, we define a list of actions.

ACTIONS = [
    HelpAction(),
    VersionAction(),

    ServerAction(),
    AdminUserAction(),
    AdminAction()
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
        action.prefix = sys.argv[0]
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

def run():
    """The fun part."""

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

    action.prefix = sys.argv[0]

    action.invoke(action.parse_arguments(sys.argv[2:]))
    
# Ideally, this would never be imported as a library, but just in case...
if __name__ == '__main__':
    run()

