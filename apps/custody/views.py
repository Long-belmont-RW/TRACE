from django.views.generic import TemplateView
from apps.accounts.mixins import RoleRequiredMixin

class OfficerDashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = ['PRISON_OFFICER', 'FACILITY_COMMANDER']
    template_name = 'custody/officer_dashboard.html'

class ManagementDashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = ['NCOS_MANAGEMENT']
    template_name = 'custody/management_dashboard.html'
