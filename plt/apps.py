from django.apps import AppConfig


class PltConfig(AppConfig):
    name = 'plt'

    def read(self):
        import plt.signals