from django.contrib import admin
from .models import Court, CourtCase, HearingLog

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'court_type')
    list_filter = ('state', 'court_type')
    search_fields = ('name',)

@admin.register(CourtCase)
class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'inmate', 'court', 'status', 'next_court_date')
    search_fields = ('case_number', 'inmate__first_name', 'inmate__last_name', 'court__name')
    list_filter = ('status', 'court')

@admin.register(HearingLog)
class HearingLogAdmin(admin.ModelAdmin):
    list_display = ('case', 'clerk', 'hearing_date', 'outcome', 'bail_amount',)
    list_filter = ('outcome', 'hearing_date')
    search_fields = ('case__case_number', 'clerk__email', 'clerk__username')
