
"""Blenderfarm database management"""

import json
import random
import string

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


class Users(DB):
    """Users database."""

    def __init__(self):
        super().__init__('users.json')
        
        self.users = []

        # If we don't have any saved data, add an admin user.
        if not self.restore():
            user = self.add('admin')
            
            print('Adding first user: "' + user.username+ '"; key ' + user.key)

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

        if self.get_user(username):
            print('attempted to add duplicate user "' + username + '"')
            return None

        key_characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
        key = ''.join(random.SystemRandom().choice(key_characters) for _ in range(16))

        user = User(username, key)

        self.users.append(user)

        self.save()
        
        return user
