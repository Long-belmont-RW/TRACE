from django.urls import path
from .views import OfficerDashboardView, ManagementDashboardView

app_name = 'custody'

urlpatterns = [
    path('officer-dashboard/', OfficerDashboardView.as_view(), name='officer_dashboard'),
    path('management-dashboard/', ManagementDashboardView.as_view(), name='management_dashboard'),
]
