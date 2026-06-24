from django.apps import AppConfig


class DoxypepConfig(AppConfig):
    name = 'doxypep'

    def ready(self):
        import doxypep.signals