from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "bc.sponsorship"

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from bc.sponsorship import signals
