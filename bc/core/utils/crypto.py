import hashlib
import random


def sha1_activation_key(s):
    """Make an activation key for a user

    :param s: The data to use with the salt to make the activation key
    :return: A SHA256 activation key
    """
    salt = hashlib.sha256(str(random.random()).encode()).hexdigest()[:5]
    activation_key = hashlib.sha256((salt + s).encode()).hexdigest()
    return activation_key
