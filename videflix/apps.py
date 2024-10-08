from django.apps import AppConfig


class VideflixConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videflix'

    def ready(self):
        import videflix.signals