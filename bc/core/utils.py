from django.db import OperationalError, connections


def check_postgresql() -> bool:
    """Just check if we can connect to postgresql"""
    try:
        for alias in connections:
            with connections[alias].cursor() as c:
                c.execute("SELECT 1")
                c.fetchone()
    except OperationalError:
        return False
    return True
