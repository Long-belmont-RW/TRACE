from django.db import models
from django.conf import settings

class Facility(models.Model):
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    commander = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'FACILITY_COMMANDER'}
    )

    class Meta:
        verbose_name_plural = 'facilities'
    def __str__(self):
        return self.name

class Inmate(models.Model):
    inmate_number = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='inmates')
    admission_date = models.DateField()
    is_active = models.BooleanField(default=True)
    has_overdue_flag = models.BooleanField(default=False)
    last_court_update = models.DateField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.inmate_number})"

class SystemAlert(models.Model):
    inmate = models.ForeignKey(Inmate, on_delete=models.CASCADE, related_name='alerts')
    date_flagged = models.DateTimeField(auto_now_add=True)
    alert_type = models.CharField(max_length=100, default='90_DAY_OVERDUE')
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Alert: {self.alert_type} for {self.inmate}"
