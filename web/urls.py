"""
URL configuration for web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from web import views
from xauth import views as auth_views

handler400 = "web.errors_views.handler_400_view"
handler403 = "web.errors_views.handler_403_view"
handler404 = "web.errors_views.handler_404_view"
handler500 = "web.errors_views.handler_500_view"

MEDIA_ROOT = getattr(settings, "MEDIA_ROOT")
MEDIA_URL = getattr(settings, "MEDIA_URL")
ONLINE = getattr(settings, "ONLINE")

urlpatterns = [
    path("", views.CustomRedirectView.as_view(), name="redirect-index"),
    # path(
    #     "sitemap.xml",
    #     sitemap,
    #     {"sitemaps": sitemaps},
    #     name="django.contrib.sitemaps.views.sitemap",
    # ),
    path("home/", views.IndexTemplateView.as_view(), name="index-view"),
    path("admin/", admin.site.urls),
    path("parameters/", include("parameter.urls")),
    path("import-export/", include("ie_app.urls")),
    path("auth/", include("xauth.urls")),
    path("login/", auth_views.CustomLoginView.as_view(), name="user-login"),
    path("signup/", auth_views.User2CreateView.as_view(), name="user-signup"),
    path("logout/", auth_views.CustomLogoutView.as_view(), name="user-logout"),
    path(
        "account-activation/<uuid:pk>/set-password/",
        auth_views.SetPasswordView.as_view(),
        name="user-set-password",
    ),
    path(
        "password-reset/request/",
        auth_views.CustomPasswordResetView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/request-done/",
        auth_views.CustomPasswordResetDoneView.as_view(),
        name="password-reset-request-done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.CustomPasswordResetCompleteView.as_view(),
        name="password-reset-complete",
    ),


] + static(MEDIA_URL, document_root=MEDIA_ROOT)
