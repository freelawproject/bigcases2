from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "bc.channel"

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from bc.channel import signals
