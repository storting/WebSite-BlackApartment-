from django.apps import AppConfig


class BlackappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BlackApp'

    def ready(self):
            # Импортируем сигналы, чтобы они зарегистрировались
            import BlackApp.signals


