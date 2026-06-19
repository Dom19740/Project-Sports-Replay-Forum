from django.apps import AppConfig


class GamifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gamify'

    def ready(self):
        import gamify.signals  # noqa: F401
