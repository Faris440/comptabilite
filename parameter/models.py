from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
# Create your models here.
from SIGC.cmodels import (
    ParameterModel,
    CONSTRAINT,
    CommonAbstractModel,
    AutoSlugField,
    StatusModel,
    CommonAbstractModelWithCodeModel,
)
from SIGC.constants import MIN_LENGTH, MEDIUM_LENGTH, BIG_LENGTH
from model_utils.choices import Choices
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _



# Définitions des longueurs par convention
Max_length = 100
Medium_length = 50
Min_length = 25

# Modèle de base avec des champs communs
class BaseModel(CommonAbstractModel):
    code = models.CharField('code', max_length=Min_length, unique=True)
    label = models.CharField(max_length=Max_length, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        abstract = True  # Modèle abstrait pour être réutilisé
class MailContent(CommonAbstractModel):
    slug = AutoSlugField(
        populate_from="label", always_update=True, max_length=MEDIUM_LENGTH, unique=True
    )
    label = models.CharField("Libellé", max_length=MEDIUM_LENGTH, unique=True)

    class Meta:
        abstract = True
