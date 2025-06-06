from django.db import models
from django.contrib.auth.models import User
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
    SoftDeletableModel,
    StatusModel,
)
from model_utils.choices import Choices
from autoslug import AutoSlugField


from SIGC.constants import LONG_LENGTH, MEDIUM_LENGTH, MIN_LENGTH





from django.db import models
from django.contrib.auth.models import User
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
    SoftDeletableModel,
    StatusModel,
)
from model_utils.choices import Choices
from autoslug import AutoSlugField


from SIGC.constants import LONG_LENGTH, MEDIUM_LENGTH, MIN_LENGTH

CONSTRAINT = models.PROTECT


class CommonAbstractModel(TimeStampedModel, UUIDModel, SoftDeletableModel):
    is_active = models.BooleanField("Est actif", default=True)
    class Meta:
        abstract = True


class CommonAbstractModelWithCodeModel(CommonAbstractModel):
    code = models.CharField(
        max_length=MIN_LENGTH,
        unique=True,
        help_text="Code unique permettant d'identifier cet élément",
        default=''
    )
    class Meta:
        abstract = True

class CommonAbstractModelWithCodeModelDeux(CommonAbstractModel):
    code = models.CharField(
        max_length=MIN_LENGTH,
        help_text="Code unique permettant d'identifier cet élément",
        default=''
    )
    class Meta:
        abstract = True

class ParameterModel(CommonAbstractModelWithCodeModel):
    label = models.CharField("Libellé", max_length=MEDIUM_LENGTH)
    description = models.TextField("Description", null=True, blank=True)
    slug = AutoSlugField(
        populate_from="label",
        always_update=True,
        max_length=LONG_LENGTH,
        unique=False,
        null=False,
        blank=True,
    )
    class Meta:
        abstract = True
    def __str__(self):
        return self.label
    
class ParameterModelDeux(CommonAbstractModelWithCodeModelDeux):
    label = models.CharField("Libellé", max_length=MEDIUM_LENGTH)
    description = models.TextField("Description", null=True, blank=True)
    slug = AutoSlugField(
        populate_from="label",
        always_update=True,
        max_length=LONG_LENGTH,
        unique=True,
        null=False,
        blank=True,
    )
    class Meta:
        abstract = True
    def __str__(self):
        return self.label
    
class ParameterSimpleModel(TimeStampedModel, UUIDModel, SoftDeletableModel):
    label = models.CharField("Libellé", max_length=MEDIUM_LENGTH, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    slug = AutoSlugField(
        populate_from="label",
        always_update=True,
        max_length=LONG_LENGTH,
        unique=True,
        null=False,
        blank=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.label


