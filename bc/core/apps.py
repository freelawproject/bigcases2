from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "bc.core"

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from bc.core import signals
