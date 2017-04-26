
"""Computes digest values for a given string."""

import hmac

def get_digest(string, user_key):
    """Returns the HMAC digest for `string`, given the key `user_key`."""
    
    return hmac.new(key=bytes(user_key, 'utf8'), msg=bytes(string, 'utf8')).hexdigest()

def get_key_value_digest(data, user_key):
    """Returns the HMAC digest for the URL and POST params `data`, given
the key `user_key`."""
    
    string = []
    
    for key in sorted(data):
        string.append(key + ':' + data[key])

    string = 'BLENDERFARM' + '\n'.join(string)
    
    return get_digest(string, user_key)

def compare(a, b): # pylint: disable=invalid-name
    """Returns `True` if `a` and `b` match; `False` otherwise."""
    
    return hmac.compare_digest(a, b)
