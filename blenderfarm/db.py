
"""Blenderfarm database management"""

import json
import random
import string

def generate_key():
    """Generates a 16-character random key."""

    key_characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(key_characters) for _ in range(16))

def generate_uuid():
    """Generates a 32-character random UUID."""

    key_characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(key_characters) for _ in range(32))

# # Abstract DB class
    
class DB:
    """Generic database abstract class."""

    def __init__(self, filename):
        self.filename = filename

    # # Save/restore

    def save(self):
        """Saves the db to disk."""

        with open(self.filename, 'w') as dbfile:
            json.dump(self._save(), dbfile)

    def restore(self):
        """Restores the db from disk. Returns `True` if restoration happened,
`False` otherwise."""

        try:
            with open(self.filename, 'r') as dbfile:
                self._restore(json.load(dbfile))
            return True
        except FileNotFoundError:
            #print('"' + self.filename + '" not saved yet; nothing to restore')
            return False

    def refresh(self):
        """Attempts to re-read the database on disk in case of changes."""

        self.restore()

    # pylint: disable=no-self-use
    def _save(self):
        """Returns a Python object to be JSON stringified."""
        return {}

    def _restore(self, data):
        """Populates the data with the Python object returned by `_save`."""
        pass


class User:
    """Single user. Basically stores data for `Users`."""

    def __init__(self, username=None, key=None):
        self.username = username
        self.key = key

    def save(self):
        """Dumps to a Python object."""

        return {
            'username': self.username,
            'key': self.key
        }

    def restore(self, data):
        """Restores from a Python object."""

        self.username = data['username']
        self.key = data['key']

    def get_username_key(self):
        """Returns a human-readable username/key string."""
        return self.username.ljust(24) + ' ' + self.key

    
# # Users

class Users(DB):
    """Users database."""

    def __init__(self):
        super().__init__('users.json')

        self.users = []

        # If we don't have any saved data, save the DB.
        if not self.restore():
            self.save()

    # # Save/restore

    def _save(self):
        out_users = []

        for user in self.users:
            out_users.append(user.save())

        return out_users

    def _restore(self, data):
        self.users = []

        for user_data in data:
            user = User()
            user.restore(user_data)

            self.users.append(user)

    def get_users(self):
        """Returns a list of every user stored in this database."""
        return self.users

    def get_user(self, username):
        """Returns the appropriate `User`, or `None` if no such user
exists."""

        self.refresh()

        for user in self.users:
            if user.username == username:
                return user

        return None

    def add(self, username):
        """Creates a user with username `username` and generates a random
key. Returns the newly created `User` or `None` if no user was created."""

        self.refresh()

        if self.get_user(username):
            print('attempted to add duplicate user "' + username + '"')
            return None

        user = User(username, generate_key())

        self.users.append(user)

        self.save()

        return user

    def remove(self, username):
        """Removes a user. Returns `False` if the user did not exist, `True` otherwise."""

        self.refresh()

        user = self.get_user(username)

        if not user:
            print('attempted to remove user "' + username + '" who does not exist')
            return False

        self.users.remove(user)

        self.save()

        return True

    def rekey(self, username):
        """Creates a new key for user `username`, discarding the old key
permanently. Returns `True` if user now has a new key, `False`
otherwise."""

        self.refresh()

        user = self.get_user(username)

        if not user:
            print('attempted to rekey user "' + username + '" who does not exist')
            return False

        user.key = generate_key()

        self.save()

        return True

