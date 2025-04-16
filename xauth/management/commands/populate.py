from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()

class Command(BaseCommand):
    help = "Commande pour remplir la base de données avec les données de paramétrage."

    def handle(self, *args, **options):
        if not User.objects.filter(matricule="admin").exists():
            User.objects.create_superuser(
                username="admin",
                password="password",
                first_name="super",
                last_name="user",
                email="admin02@hotmail.com",
                birthdate=timezone.now(),
                birthplace="Ouagadougou",
                matricule="N12345L",
                phone="70010203",
            )

        self.set_permissions()
        # self.schedule_sending_mail()

        self.stdout.write(self.style.SUCCESS("Donné ajouté avec succès"))

    def set_permissions(self):

        Permission.objects.get_or_create(
            codename="list_group",
            name="Can list group",
            content_type=ContentType.objects.get_for_model(Group),
        )

        self.stdout.write(self.style.SUCCESS("permissions ajoutées"))
