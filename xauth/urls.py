from django.urls import include, path

from xauth import views

app_name = "auth"

urlpatterns = [
    # User
    path("users/create/", views.UserCreateView.as_view(), name="user-create"),


    path("users/list/", views.UserListView.as_view(), name="user-list"),
  
    path("users/staff/list/", views.StaffListView.as_view(), name="staff-list"),
    path(
        "users/<uuid:pk>/edit/",
        views.UserUpdateView.as_view(),
        name="user-update",
    ),
    path(
        "users/<uuid:pk>/edit/photo",
        views.UserProfilePhotoUpdateView.as_view(),
        name="user-update-photo",
    ),
    path(
        "users/<uuid:pk>/detail/",
        views.UserDetailView.as_view(),
        name="user-detail",
    ),
    path(
        "users/<uuid:pk>/delete/",
        views.UserDeleteView.as_view(),
        name="user-delete",
    ),
    path(
        "users/<uuid:pk>/password/",
        views.UserUpdatePasswordView.as_view(),
        name="user-update-password",
    ),
    path(
        "users/<uuid:pk>/make-admin/",
        views.UserAdminRightView.as_view(),
        name="user-make-admin",
    ),
    path(
        "users/<uuid:pk>/send-activation-key/",
        views.UserSendSecreteKey.as_view(),
        name="user-send-key",
    ),
    # Group
    path("groups/create/", views.GroupCreateView.as_view(), name="group-create"),
    path(
        "groups/<int:pk>/update/",
        views.GroupUpdateView.as_view(),
        name="group-update",
    ),
    path("groups/list/", views.GroupListView.as_view(), name="group-list"),
    path(
        "groups/<int:pk>/delete/",
        views.GroupDeleteView.as_view(),
        name="group-delete",
    ),
    path(
        "groups/<int:pk>/detail/",
        views.GroupDetailView.as_view(),
        name="group-detail",
    ),
]
