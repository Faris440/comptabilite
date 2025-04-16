from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def admin_required(view_func=None, login_url=None, raise_exception=True):
    """
    Decorator for views that checks that the user is logged in and is a
    companies users, displaying message if provided.
    """

    def auth_user(u):
        if u.has_perms(
            [
                "app.add_task",
                "app.change_task",
                "app.can_validate_task",
                "app.can_close_task",
            ]
        ):
            return True
        else:
            if raise_exception:
                raise PermissionDenied
        return False

    actual_decorator = user_passes_test(auth_user, login_url=login_url)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def superuser_required(view_func=None, login_url=None, raise_exception=True):
    """
    Decorator for views that checks that the user is logged in and is a
    companies users, displaying message if provided.
    """

    def auth_user(u):
        if not hasattr(u, "is_superuser"):
            return False
        if u.is_superuser:
            return True
        else:
            if raise_exception:
                raise PermissionDenied
        return False

    actual_decorator = user_passes_test(auth_user, login_url=login_url)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

