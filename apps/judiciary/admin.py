from django.contrib import admin
from .models import CourtCase, HearingLog

@admin.register(CourtCase)
class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'inmate', 'court_name', 'status', 'next_court_date')
    search_fields = ('case_number', 'inmate__first_name', 'inmate__last_name', 'court_name')
    list_filter = ('status', 'court_name')

@admin.register(HearingLog)
class HearingLogAdmin(admin.ModelAdmin):
    list_display = ('case', 'clerk', 'hearing_date', 'outcome', 'bail_amount')
    list_filter = ('outcome', 'hearing_date')
    search_fields = ('case__case_number', 'clerk__email', 'clerk__username')
