from django.urls import path
from .views import (
    OfficerDashboardView,
    EscalateAlertView,
    ResolveAlertView,
    FacilityReportsView,
    NcosDashboardView,
    FacilityInmatesView,
    FacilityCasesView,
    NcosFacilityDirectoryView,
    NcosFacilityInmatesView,
    NcosFacilityCasesView,
    NcosFacilityAlertsView,
    NcosGlobalSearchView,
    TriggerMidnightScanView,
    SuperadminFacilitiesListView,
)

app_name = 'custody'

urlpatterns = [
    path('officer/dashboard/', OfficerDashboardView.as_view(), name='officer_dashboard'),
    path('officer/inmates/', FacilityInmatesView.as_view(), name='facility_inmates'),
    path('officer/cases/', FacilityCasesView.as_view(), name='facility_cases'),
    path('officer/reports/', FacilityReportsView.as_view(), name='facility_reports'),
    path('management-dashboard/', NcosDashboardView.as_view(), name='management_dashboard'),
    path('management/analytics/', NcosDashboardView.as_view(), name='ncos_dashboard'),
    path('management/facilities/', NcosFacilityDirectoryView.as_view(), name='ncos_facility_directory'),
    path('management/facility/<int:facility_id>/inmates/', NcosFacilityInmatesView.as_view(), name='ncos_facility_inmates'),
    path('management/facility/<int:facility_id>/cases/', NcosFacilityCasesView.as_view(), name='ncos_facility_cases'),
    path('management/facility/<int:facility_id>/alerts/', NcosFacilityAlertsView.as_view(), name='ncos_facility_alerts'),
    path('management/search/', NcosGlobalSearchView.as_view(), name='ncos_global_search'),
    path('management/trigger-scan/', TriggerMidnightScanView.as_view(), name='trigger_midnight_scan'),
    path('superadmin/facilities/', SuperadminFacilitiesListView.as_view(), name='superadmin_facilities_list'),
    path('officer/escalate/', EscalateAlertView.as_view(), name='escalate_alert'),
    path('commander/resolve/', ResolveAlertView.as_view(), name='resolve_alert'),
]
