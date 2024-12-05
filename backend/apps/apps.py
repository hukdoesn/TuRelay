from django.apps import AppConfig

class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self):
        # Import the scheduler and start it within the ready method
        from .scheduler import start_scheduler
        start_scheduler()