from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "bc.users"

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from bc.users import signals
