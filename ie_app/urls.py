from django.urls import path

from ie_app import views

app_name = "ie_app"

urlpatterns = [
    path(
        "export/<str:model_name>/<int:with_data>/",
        views.ExportView.as_view(),
        name="export-view",
    ),
    path(
        "import/<str:model_name>/",
        view=views.ImportView.as_view(),
        name="import-view",
    ),
    path(
        "confirm-import/<str:model_name>/",
        view=views.ConfirmImportView.as_view(),
        name="confirm-import-view",
    ),
    
]
