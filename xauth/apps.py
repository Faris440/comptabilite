from django.apps import AppConfig
from django.core.signals import request_finished


class XauthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "xauth"
    verbose_name = "Application de gestion du personnelle"

    def ready(self):
        from xauth import signals
        from xauth.models import User

        request_finished.connect(
            signals.set_username, dispatch_uid="set_username", sender=User
        )
