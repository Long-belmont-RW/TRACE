from django.urls import path
from .views import ClerkDashboardView, LawyerPortalView

app_name = 'judiciary'

urlpatterns = [
    path('clerk-dashboard/', ClerkDashboardView.as_view(), name='clerk_dashboard'),
    path('lawyer-portal/', LawyerPortalView.as_view(), name='lawyer_portal'),
]
