from django.apps import AppConfig
from .signals import app_ready


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        app_ready.send(sender=self.__class__)
