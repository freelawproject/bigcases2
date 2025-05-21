from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "bc.subscription"

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from bc.subscription import signals  # noqa: F401
