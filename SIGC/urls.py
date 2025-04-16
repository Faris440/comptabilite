"""
URL configuration for SIGC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views 
from xauth import views as xauth_views
from django.views.i18n import JavaScriptCatalog



MEDIA_ROOT = getattr (settings,"MEDIA_ROOT")
MEDIA_URL = getattr (settings,"MEDIA_URL")




urlpatterns = [
    path('', views.RedirectionView.as_view(),name='redirect'),
    path('home/', views.IndexTemplateView.as_view(),name='index-view'),
    path('admin/', admin.site.urls),
    path('login/', xauth_views.CustomLoginView.as_view(), name='user-login'),
    path('logout/', xauth_views.CustomLogoutView.as_view(), name='logout'),
    path('auth/', include('xauth.urls')),
    path('parameter/', include('parameter.urls')),   
    path("signup/", xauth_views.User2CreateView.as_view(), name="user-signup"),
    path('retour/', views.back_button_view, name='back-button'),
    # path(
    #     "account-activation/<uuid:pk>/set-password/",
    #     xauth_views.SetPasswordView.as_view(),
    #     name="user-set-password",
    # ),
    path(
        "account-activation/<str:uidb64>/set-password/<str:token>",
        xauth_views.SetPasswordView.as_view(),
        name="user-set-password",
    ),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

] + static(MEDIA_URL, document_root=MEDIA_ROOT)


