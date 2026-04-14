from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "apps.notification"
    label = "notification"

    def ready(self):
        from apps.notification import signals  # noqa: F401
