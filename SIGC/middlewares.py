from django.urls import resolve
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .decorators import admin_required, superuser_required
import threading
local_user = threading.local()
import threading
local_user = threading.local()

PUBLIC_NAMED_URLS = getattr(settings, "PUBLIC_NAMED_URLS", ())
ONLY_ADMINS_URLS = getattr(settings, "ONLY_ADMINS_URLS", ())
ONLY_SUPERUSER_URLS = getattr(settings, "ONLY_SUPERUSER_URLS", ())


class UserRightMiddleware:
    def _init_(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def process_view(self, request, view_func, view_args, view_kwargs):
        url_name = resolve(request.path_info).url_name

        decorator = None
        if url_name in ONLY_ADMINS_URLS:
            decorator = admin_required()
        if url_name in ONLY_SUPERUSER_URLS:
            decorator = superuser_required()
        else:
            return None

        return decorator(view_func)(request, *view_args, **view_kwargs)

    def _call_(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def process_view(self, request, view_func, view_args, view_kwargs):
        url_name = resolve(request.path_info).url_name

        decorator = None
        if request.user.is_authenticated or (url_name in PUBLIC_NAMED_URLS):
            return None
        else:
            decorator = login_required()
            return decorator(view_func)(request, *view_args, **view_kwargs)

    def __call__(self, request):
        response = self.get_response(request)
        return response