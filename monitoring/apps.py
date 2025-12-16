# monitoring/apps.py
from django.apps import AppConfig

class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self):
        # importe les signals pour les enregistrer
        try:
            import monitoring.signals  # noqa: F401
        except Exception as e:
            print(f"Error importing signals: {e}")
