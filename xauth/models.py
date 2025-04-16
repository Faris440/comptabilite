from collections import defaultdict
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from model_utils.choices import Choices
from datetime import date, datetime
from SIGC.cmodels import CONSTRAINT, CommonAbstractModel
from SIGC.constants import MEDIUM_LENGTH, MIN_LENGTH
from parameter import models as parameter_models
from phonenumber_field.modelfields import PhoneNumberField
from SIGC.constants import BIG_LENGTH

import uuid
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField




# Create your models here.

class User(AbstractUser, CommonAbstractModel):

    USERNAME_FIELD = "matricule"
    GENDER_CHOICES = [
        ('F', 'Femme'),
        ('H', 'Homme'),
    ]
    
    MATRIAL_STATUS = Choices(
        ('bachelor', 'Célibataire'),
        ('married', 'Mariée'),
        ('divorced', 'Divorcée'),
        ('widower', 'Veuve'),
    )
    
    first_name = models.CharField(_("first name"), max_length=MEDIUM_LENGTH)
    last_name = models.CharField(_("last name"), max_length=MEDIUM_LENGTH)
    diplome = models.CharField(_("diplome"),null=True, max_length=MEDIUM_LENGTH)
    structure_origine = models.CharField(_("Struture d'origine"), max_length=MEDIUM_LENGTH)
    birthdate = models.DateField("Date de naissance")
    email = models.EmailField(_("email address"), unique=True)
    birthdate = models.DateField("Date de naissance")
    birthplace = models.CharField("Lieu de naissance", max_length=MIN_LENGTH)
    matricule = models.CharField(max_length=MIN_LENGTH, null=True, unique=True)
    address = models.CharField("Adresse", max_length=MIN_LENGTH, null=True, blank=True)
    photo = models.ImageField(
        "Photo d'identité",
        null=True,
        blank=True,
        help_text="Une image dont la taille n'excède pas 3 Mo",
        upload_to="profil/",
    )
    phone = PhoneNumberField("Numéro de téléphone", unique=True)
    marital_status = models.CharField(
        max_length=20,
        verbose_name="Situation matrimoniale",
        choices=MATRIAL_STATUS,
        default=MATRIAL_STATUS.bachelor,
    )
    nationality = models.CharField(
        verbose_name="Nationalité",
        max_length=MIN_LENGTH,
        null=True,
        blank=True
    )
    gender = models.CharField(
        "Genre",
        max_length=1,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
    )
    
    def get_role(self):
        if self.is_staff:
            return "admin"
        elif hasattr(self, "assign"):
            return self.assign.group_assign.name
        else:
            return "-"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
 
    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        permissions = [
            ("list_user", "Can list user"),
            # # ("can_assign", "Peut attribuer un rôle"),
            # ("can_assign_module", "Peut attribuer un module"),
            # ("can_unassign_module", "Peut retirer un module"),
            ("deactivate_user", "Can deactivate user"),
            ("change_right_user", "Can change user right"),
            # ("access_parameter", "Can access to parameter module"),
            # ("access_fiche_management", "Can access to fiche_management module"),
            ("access_xauth", "Can access to xauth module"),
            # ("access_account", "Can access to account module"),
            # ("can_submit_programmatic_sheet", "Peut soumettre une fiche programmatique"),
            # ("can_update_programmatic_sheet", "Peut modifier une fiche programmatique"),
            # ("can_delete_programmatic_sheet", "Peut supprimer une fiche programmatique"),
            # ("can_download_programmatic_sheet", "peut telecharger une fiche programmatique"),
            # ("can_export_programmatic_sheet", "Peut exporter une fiche programmatique"),
            # ("can_validate_programmatic_sheet", "peut valider une fiche programmatique"),
            # ("vice_president", "Est un vice président"),
            # ("responsable_ufr", "Est responsable d'une ufr"),
            # ("responsable_programme", "Est responsable d'un programme"),
            # ("responsable_filiere", "Est responsable d'une filière"),
        ]

class AccountActivationSecret(CommonAbstractModel):
    user = models.OneToOneField(User, on_delete=CONSTRAINT)
    secret = models.CharField(max_length=MIN_LENGTH)


class Assign(CommonAbstractModel):
    assigner = models.ForeignKey(
        User, on_delete=CONSTRAINT, related_name="assigner", null=True, blank=True
    )
    unassigner = models.ForeignKey(
        User, on_delete=CONSTRAINT, related_name="unassigner", null=True, blank=True
    )
    
    user = models.OneToOneField(
        User, on_delete=CONSTRAINT, related_name="assign", null=True, blank=True
    )

    nomination_date = models.DateField(null=True)
    effective_date = models.DateField(null=True)
    end_date = models.DateField(null=True, blank=True)
    group_assign = models.ForeignKey(
        "auth.Group", on_delete=CONSTRAINT, null=True, blank=True
    )

# class Nomination(CommonAbstractModel):
#     # Champ ForeignKey pour l'utilisateur (non nullable)
#     user = models.ForeignKey(
#         User,  # Si vous utilisez le modèle utilisateur par défaut de Django
#         on_delete=models.CASCADE,
#         related_name="nominations",
#         null=False
#     )

#     # Champ de type choix pour la nomination
#     NOMINATION_TYPE_CHOICES = [
#         ('filiere', 'Filière'),
#         ('ufr', 'UFR'),
#         ('vise-president', 'Vice-président'),
#     ]
#     nomination_type = models.CharField(
#         max_length=20,
#         choices=NOMINATION_TYPE_CHOICES,
#         null=False
#     )

#     # Champs ForeignKey pour les différentes entités (ufr, departement, filiere) avec possibilité d'être null
#     ufr = models.ForeignKey(
#         'parameter.UniteDeRecherche',  # Remplacez par le modèle réel pour UFR
#         on_delete=models.SET_NULL,
#         related_name="nominations_ufr",
#         null=True,
#         blank=True
#     )
    
#     departement = models.ForeignKey(
#         'parameter.Departement',  # Remplacez par le modèle réel pour Département
#         on_delete=models.SET_NULL,
#         related_name="nominations_departement",
#         null=True,
#         blank=True
#     )

#     filiere = models.ForeignKey(
#         'parameter.Filiere',        # Remplacez par le modèle réel pour Filière
#         on_delete=models.SET_NULL,
#         related_name="nominations_filiere",
#         null=True,
#         blank=True
#     )

#     # Champ date_debut qui est obligatoire
#     date_debut = models.DateField(null=False)
#     date_fin = models.DateField(null=True)
#     is_desactivate = models.BooleanField("Est inactif", default=False)

#     def __str__(self):
#         return f"Nomination de {self.user} pour {self.nomination_type} - {self.date_debut}"

#     class Meta:
#         verbose_name = "Nomination"
#         verbose_name_plural = "Nominations"
#         ordering = ['date_debut']



# class AttributModule(CommonAbstractModel):
    
#      # Champ ForeignKey pour l'utilisateur (non nullable)
#     user = models.ForeignKey(
#         User,  # Si vous utilisez le modèle utilisateur par défaut de Django
#         on_delete=models.CASCADE,
#         related_name="assignations_modules",
#         null=False
#     )
#     module = models.ForeignKey(
#         'parameter.Module',
#         on_delete=models.SET_NULL,        
#         related_name="assignation_module",
#         null=True,
#         blank=True
#     )
#     def __str__(self):
#         return f"Attribution de {self.module} pour la filiere {self.filiere} à l'enseignant "

#     class Meta:
#             verbose_name = "assignation de module"
#             verbose_name_plural = "attributions de modules"



# class AttributModule(CommonAbstractModel):
#     # Champ ForeignKey pour l'utilisateur (non nullable)
#     user = models.ForeignKey(
#         User,  # Si vous utilisez le modèle utilisateur par défaut de Django
#         on_delete=models.CASCADE,
#         related_name="assignations_modules",
#         null=False
#     )

#     filiere = models.ForeignKey(
#         'parameter.Filiere',       
#         on_delete=models.SET_NULL,
#         related_name="assignation_filiere",
#         null=True,
#         blank=True
#     )
#     module = models.ForeignKey(
#         'parameter.Module',
#         on_delete=models.SET_NULL,        
#         related_name="assignation_module",
#         null=True,
#         blank=True
#     )
#     def __str__(self):
#         return f"Attribution du module de {self.module} à l'enseignant {self.user} "

#     class Meta:
#         verbose_name = "Assignation_de_module"
#         verbose_name_plural = "Assignation_de_modules"

