from django.views.generic import TemplateView
from apps.accounts.mixins import RoleRequiredMixin

class ClerkDashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = ['COURT_CLERK']
    template_name = 'judiciary/clerk_dashboard.html'

class LawyerPortalView(RoleRequiredMixin, TemplateView):
    allowed_roles = ['LAWYER']
    template_name = 'judiciary/lawyer_portal.html'
