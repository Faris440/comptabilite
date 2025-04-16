from django.core.management.base import BaseCommand
from xauth.models import User  # Assurez-vous de remplacer 'yourapp' par le nom réel de votre application
from parameter.models import Service  # Assurez-vous que 'parameter' est l'app où le modèle Service est défini.
import random
from faker import Faker
from faker.providers import BaseProvider

# Liste des prénoms, noms de famille et préfixes téléphoniques burkinabé
burkinabe_first_names = [
    "Aïcha", "Abdoulaye", "Alima", "Assita", "Bintou", "Fanta", "Fatoumata", 
    "Issa", "Koumba", "Moussa", "Oumar", "Seydou", "Souleymane", "Yacouba", "Youssouf"
]

burkinabe_last_names = [
    "Ouédraogo", "Zongo", "Sawadogo", "Kaboré", "Sorgho", "Bationo", "Ouedraogo", 
    "Kaboré", "Compaoré", "Konaté", "Diallo", "Sanogo", "Sanou", "Kouanda", "Nikiema"
]

burkinabe_phone_prefixes = [
    '70', '71', '72', '73', '74', '75', '76', '77', '78', '79'
]

class BurkinabeNameProvider(BaseProvider):
    def burkinabe_first_name(self):
        return random.choice(burkinabe_first_names)

    def burkinabe_last_name(self):
        return random.choice(burkinabe_last_names)

    def burkinabe_phone_number(self):
        prefix = random.choice(burkinabe_phone_prefixes)
        number = ''.join(random.choices('0123456789', k=6))
        return f'+226{prefix}{number}'

class Command(BaseCommand):
    help = 'Create initial users'

    def handle(self, *args, **kwargs):
        fake = Faker()
        fake.add_provider(BurkinabeNameProvider)
        service = Service.objects.first()  # Assurez-vous qu'il existe au moins un Service

        if not service:
            self.stdout.write(self.style.ERROR('No Service found. Please create one first.'))
            return

        for i in range(8):
            is_patient = random.choice([True, False])
            is_praticient = not is_patient

            user = User.objects.create(
                first_name=fake.burkinabe_first_name(),
                last_name=fake.burkinabe_last_name(),
                email=fake.email(),
                birthdate=fake.date_of_birth(minimum_age=18, maximum_age=90),
                birthplace=fake.city(),
                matricule=fake.unique.bothify(text='??#####'),
                address=fake.address(),
                phone=fake.burkinabe_phone_number(),
                is_patient=is_patient,
                is_praticient=is_praticient,
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created 8 users'))
