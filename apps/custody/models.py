from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class NigerianStates(models.TextChoices):
    ABIA = 'AB', _('Abia')
    ADAMAWA = 'AD', _('Adamawa')
    AKWA_IBOM = 'AK', _('Akwa Ibom')
    ANAMBRA = 'AN', _('Anambra')
    BAUCHI = 'BA', _('Bauchi')
    BAYELSA = 'BY', _('Bayelsa')
    BENUE = 'BE', _('Benue')
    BORNO = 'BO', _('Borno')
    CROSS_RIVER = 'CR', _('Cross River')
    DELTA = 'DE', _('Delta')
    EBONYI = 'EB', _('Ebonyi')
    EDO = 'ED', _('Edo')
    EKITI = 'EK', _('Ekiti')
    ENUGU = 'EN', _('Enugu')
    FCT = 'FC', _('Federal Capital Territory')
    GOMBE = 'GO', _('Gombe')
    IMO = 'IM', _('Imo')
    JIGAWA = 'JI', _('Jigawa')
    KADUNA = 'KD', _('Kaduna')
    KANO = 'KN', _('Kano')
    KATSINA = 'KT', _('Katsina')
    KEBBI = 'KE', _('Kebbi')
    KOGI = 'KO', _('Kogi')
    KWARA = 'KW', _('Kwara')
    LAGOS = 'LA', _('Lagos')
    NASARAWA = 'NA', _('Nasarawa')
    NIGER = 'NI', _('Niger')
    OGUN = 'OG', _('Ogun')
    ONDO = 'ON', _('Ondo')
    OSUN = 'OS', _('Osun')
    OYO = 'OY', _('Oyo')
    PLATEAU = 'PL', _('Plateau')
    RIVERS = 'RI', _('Rivers')
    SOKOTO = 'SO', _('Sokoto')
    TARABA = 'TA', _('Taraba')
    YOBE = 'YO', _('Yobe')
    ZAMFARA = 'ZA', _('Zamfara')

class Facility(models.Model):
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=2, choices=NigerianStates.choices)
    commander = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'FACILITY_COMMANDER'},
        related_name='commanded_facilities'
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
    updated_at = models.DateTimeField(auto_now=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    alert_type = models.CharField(max_length=100, default='90_DAY_OVERDUE')
    is_resolved = models.BooleanField(default=False)
    is_escalated = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def get_status_display(self):
        if self.is_resolved:
            return "Resolved"
        elif self.is_escalated:
            return "Escalated"
        return "Flagged"

    def __str__(self):
        return f"Alert: {self.alert_type} for {self.inmate}"
