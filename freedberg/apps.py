from django.apps import AppConfig


class FreedbergConfig(AppConfig):
    name = 'freedberg'

    def ready(self):
        import freedberg.signals