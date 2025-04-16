from django.contrib.auth import models as auth_models
from django.utils import timezone
from django.contrib import messages
from import_export.widgets import CharWidget

from import_export import fields, resources, widgets, results
from phonenumber_field.phonenumber import PhoneNumber

from xauth.models import User
from parameter import models as parameter_models

# from workforce import models as workforce_models
from web import mails


fields_name = {
    "label": "libellé",
    "first_name": "prénom(s)",
    "last_name": "nom(s)",
    "category": "catégorie",
    "phone": "téléphone",
    "start_at": "date de début",
    "end_at": "date de fin",
    "username": "nom d'utilisateur",
    "email": "courriel",
    "priority": "priorité",
    "is_closed": "est close",
    "is_validated": "est validé",
    "was_reopened": "a été re-ouvert",
    "is_pending": "est suspendu",
    "create_at": "enregistré le",
    "close_at": "clos le",
    "deadline": "date de rigueur",
    "is_active": "est actif",
    "author": "auteur(s)",
    "writer": "rédacteur",
    "assigned_to": "assigné à",
    "value": "valuer",
}


class PhoneNumberWidget(widgets.Widget):
    def clean(self, value, row=None, **kwargs):
        phone = PhoneNumber.from_string(str(value))

        return phone


class CustomModelResource(resources.ModelResource):
    def __init__(self, **kwargs):
        self.with_data = kwargs.pop("with_data", 1)
        super().__init__(**kwargs)

    def get_export_headers(self, fields=None):
        if fields is None:
            fields = self.get_fields()
        headers = [field.column_name for field in fields]
        return headers

    """def get_export_headers(self):
        headers = super().get_export_headers()
        if self.with_data != 1:
            return headers
        headers = [
            fields_name.get(str(header), str(header)).capitalize() for header in headers
        ]
        return headers"""

    def get_none(self):
        return self._meta.model.objects.none()





class RegionResource(CustomModelResource):
    class Meta:
        model = parameter_models.Region
        import_id_fields = ('code',)
        fields = ['code', 'label', 'region_place', 'description']



class UserResource(CustomModelResource):

    phone = fields.Field(
        column_name="phone", attribute="phone", widget=PhoneNumberWidget()
    )

    def before_save_instance(self, instance, row, **kwargs):
            instance.is_active = False
    # def after_import_row(
    #     self, row, row_result: results.RowResult, row_number=None, **kwargs
    # ):
    #     if "request" in kwargs:
    #         pass

    class Meta:
        model = User
class GroupResource(CustomModelResource):
    permissions = fields.Field(
        column_name="permissions",
        attribute="permissions",
        widget=widgets.ManyToManyWidget(auth_models.Permission, field="name"),
    )

    class Meta:
        model = auth_models.Group
        fields = ["name", "permissions"]


class_list = [User, auth_models.Group,parameter_models.Region]
resource_classes = {
    model.__name__: eval(model.__name__ + "Resource") for model in class_list
}
resource_classes.update({"default": CustomModelResource})
