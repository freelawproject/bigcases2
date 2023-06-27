from hashlib import sha256

from .models import User


def convert_to_stub_account(user: User) -> User:
    """Set all fields to as blank as possible.

    :param user: The user to operate on.
    :return: The new user object.
    """
    user.first_name = "Deleted"
    user.last_name = ""
    user.affiliation = ""
    user.is_active = False
    user.username = sha256(user.email.encode()).hexdigest()
    user.set_unusable_password()
    user.save()

    return user
