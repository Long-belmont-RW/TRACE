import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from faker import Faker

from apps.custody.models import Facility, Inmate, SystemAlert
from apps.judiciary.models import Court, CourtCase, HearingLog

User = get_user_model()
fake = Faker('en_NG')

class Command(BaseCommand):
    help = 'Seeds initial realistic data for TRACE using Faker for a stakeholder pitch'

    def handle(self, *args, **options):
        password = 'TracePitch2026!'

        self.stdout.write("Clearing existing data...")
        SystemAlert.objects.all().delete()
        HearingLog.objects.all().delete()
        CourtCase.objects.all().delete()
        Inmate.objects.all().delete()
        Facility.objects.all().delete()
        Court.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # Task 2: Infrastructure Seeding
        facilities_data = [
            {"name": "Kuje Medium Security", "state": "FC"},
            {"name": "Ikoyi Custodial Centre", "state": "LA"},
            {"name": "Kaduna Convict Prison", "state": "KD"},
            {"name": "Jos Custodial Centre", "state": "PL"}
        ]

        courts_data = [
            {"name": "Federal High Court, Abuja", "state": "FC", "court_type": "Federal High"},
            {"name": "Lagos State High Court", "state": "LA", "court_type": "State High"},
            {"name": "Kaduna Magistrate Court", "state": "KD", "court_type": "Magistrate"},
            {"name": "Jos State High Court", "state": "PL", "court_type": "State High"}
        ]

        self.stdout.write("Seeding Facilities & Courts...")
        facilities = []
        for data in facilities_data:
            facilities.append(Facility.objects.create(**data))
            
        courts = []
        for data in courts_data:
            courts.append(Court.objects.create(**data))

        # Task 3: User Seeding (The Staff)
        self.stdout.write("Seeding Staff (Users)...")
        lawyer_email = 'lawyer@trace.gov.ng'
        User.objects.create_user(email=lawyer_email, password=password, role='LAWYER')

        demo_commander = None
        demo_officer = None
        for fac in facilities:
            slug = slugify(fac.name).replace('-', '_')
            commander_email = f"commander_{slug}@trace.gov.ng"
            cmd = User.objects.create_user(email=commander_email, password=password, role='FACILITY_COMMANDER', facility=fac)
            fac.commander = cmd
            fac.save()
            
            officer_email = f"officer_{slug}@trace.gov.ng"
            off = User.objects.create_user(email=officer_email, password=password, role='PRISON_OFFICER', facility=fac)

            if not demo_commander:
                demo_commander = commander_email
                demo_officer = officer_email

        demo_clerk = None
        for court in courts:
            slug = slugify(court.name).replace('-', '_')
            clerk_email = f"clerk_{slug}@trace.gov.ng"
            User.objects.create_user(email=clerk_email, password=password, role='COURT_CLERK', court=court)

            if not demo_clerk:
                demo_clerk = clerk_email

        # Task 4: Entity Seeding (Inmates & Cases)
        self.stdout.write("Seeding Realistic Inmates and Court Cases by Facility...")
        
        # Ensure a completely clean slate before the loop (redundant but requested)
        CourtCase.objects.all().delete()
        Inmate.objects.all().delete()

        charges = ["Theft", "Fraud", "Assault", "Cybercrime"]
        today = datetime.date.today()

        for fac in facilities:
            # Seed Overdue Inmates (The Red Flags)
            num_overdue = random.randint(30, 40)
            for _ in range(num_overdue):
                last_court_update = today - datetime.timedelta(days=random.randint(95, 180))
                inmate = Inmate.objects.create(
                    inmate_number=f"TRC-{fake.unique.random_int(100000, 999999)}",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    facility=fac,
                    admission_date=fake.date_between(start_date='-2y', end_date='-181d'),
                    last_court_update=last_court_update
                )

                CourtCase.objects.create(
                    case_number=f"SUIT-{fake.unique.random_int(100000, 999999)}",
                    inmate=inmate,
                    court=random.choice(courts),
                    charge_summary=random.choice(charges),
                    status='ONGOING',
                    next_court_date=fake.date_between(start_date='today', end_date='+60d')
                )

            # Seed Compliant Inmates (The Safe Zone)
            for _ in range(20):
                last_court_update = today - datetime.timedelta(days=random.randint(5, 80))
                inmate = Inmate.objects.create(
                    inmate_number=f"TRC-{fake.unique.random_int(100000, 999999)}",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    facility=fac,
                    admission_date=fake.date_between(start_date='-2y', end_date='-81d'),
                    last_court_update=last_court_update
                )

                CourtCase.objects.create(
                    case_number=f"SUIT-{fake.unique.random_int(100000, 999999)}",
                    inmate=inmate,
                    court=random.choice(courts),
                    charge_summary=random.choice(charges),
                    status='ONGOING',
                    next_court_date=fake.date_between(start_date='today', end_date='+60d')
                )

        # Task 5: Output
        self.stdout.write(self.style.SUCCESS("Successfully seeded TRACE database with Faker!"))
        self.stdout.write("\n=== Demo Credentials ===")
        self.stdout.write(f"Password for all: {password}")
        self.stdout.write(f"Lawyer: {lawyer_email}")
        self.stdout.write(f"Commander: {demo_commander}")
        self.stdout.write(f"Officer: {demo_officer}")
        self.stdout.write(f"Clerk: {demo_clerk}")
        self.stdout.write("========================\n")
