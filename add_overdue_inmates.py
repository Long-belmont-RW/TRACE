import os
import django
import random
import sys
from faker import Faker

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.custody.models import Facility, Inmate
from apps.judiciary.models import CourtCase, Court

fake = Faker('en_NG')

facilities = Facility.objects.all()
courts = Court.objects.all()

if not courts.exists() or not facilities.exists():
    print("Error: No facilities or courts found. Did you run the seed script?")
    sys.exit(1)

charges = ["Theft", "Fraud", "Assault", "Cybercrime"]

print(f"Adding 15 overdue inmates to {facilities.count()} facilities...")

for facility in facilities:
    for _ in range(15):
        last_court_update = fake.date_between(start_date='-150d', end_date='-100d')
        admission_date = fake.date_between(start_date='-2y', end_date='-160d')

        inmate = Inmate.objects.create(
            inmate_number=f"TRC-OD-{fake.random_int(10000, 99999)}",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            facility=facility,
            admission_date=admission_date,
            last_court_update=last_court_update
        )

        CourtCase.objects.create(
            case_number=f"SUIT-OD-{fake.random_int(1000, 9999)}",
            inmate=inmate,
            court=random.choice(courts),
            charge_summary=random.choice(charges),
            status='ONGOING',
            next_court_date=fake.date_between(start_date='today', end_date='+60d')
        )

print("Successfully added 60 overdue inmates and cases.")
