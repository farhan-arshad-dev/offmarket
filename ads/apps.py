from django.apps import AppConfig


class AdsConfig(AppConfig):
    name = "ads"

    def ready(self):
        from ads import signals  # noqa F401
