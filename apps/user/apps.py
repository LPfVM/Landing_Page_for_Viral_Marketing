from django.apps import AppConfig


class UserConfig(AppConfig):
    name = "apps.user"
    label = "user"

    def ready(self):
        import apps.user.signals  # noqa: F401
