from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.custody.models import Inmate, NigerianStates

class CourtTypeChoices(models.TextChoices):
    SUPREME = 'Supreme', 'Supreme'
    APPEAL = 'Appeal', 'Appeal'
    FEDERAL_HIGH = 'Federal High', 'Federal High'
    STATE_HIGH = 'State High', 'State High'
    MAGISTRATE = 'Magistrate', 'Magistrate'
    CUSTOMARY = 'Customary', 'Customary'

class Court(models.Model):
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=2, choices=NigerianStates.choices)
    court_type = models.CharField(max_length=50, choices=CourtTypeChoices.choices)

    def __str__(self):
        return f"{self.name} ({self.get_court_type_display()})"

class CourtCase(models.Model):
    STATUS_CHOICES = [
        ('ONGOING', 'Ongoing'),
        ('DISMISSED', 'Dismissed'),
        ('CONVICTED', 'Convicted'),
    ]

    case_number = models.CharField(max_length=100, unique=True, db_index=True)
    inmate = models.ForeignKey(Inmate, on_delete=models.CASCADE, related_name='cases')
    court = models.ForeignKey(Court, on_delete=models.SET_NULL, null=True, related_name='cases')
    charge_summary = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ONGOING')
    next_court_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.case_number} - {self.inmate}"

class HearingLog(models.Model):
    OUTCOME_CHOICES = [
        ('BAIL_GRANTED', 'Bail Granted'),
        ('ADJOURNED', 'Adjourned'),
        ('DISMISSED', 'Dismissed'),
        ('SENTENCED', 'Sentenced'),
    ]

    case = models.ForeignKey(CourtCase, on_delete=models.CASCADE, related_name='hearings')
    clerk = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'COURT_CLERK'}
    )
    hearing_date = models.DateTimeField(default=timezone.now)
    outcome = models.CharField(max_length=50, choices=OUTCOME_CHOICES)
    bail_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bail_conditions = models.TextField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Hearing for {self.case.case_number} on {self.hearing_date.date()}"
