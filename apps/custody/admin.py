from django.contrib import admin
from .models import Facility, Inmate, SystemAlert

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'commander')
    search_fields = ('name', 'state', 'commander__email')
    list_filter = ('state',)

@admin.register(Inmate)
class InmateAdmin(admin.ModelAdmin):
    list_display = ('inmate_number', 'first_name', 'last_name', 'facility', 'admission_date', 'is_active', 'has_overdue_flag')
    search_fields = ('inmate_number', 'first_name', 'last_name')
    list_filter = ('is_active', 'has_overdue_flag', 'facility')

@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ('inmate', 'alert_type', 'date_flagged', 'is_resolved', 'resolved_by')
    list_filter = ('is_resolved', 'alert_type', 'date_flagged')
    search_fields = ('inmate__inmate_number', 'inmate__first_name', 'inmate__last_name')
