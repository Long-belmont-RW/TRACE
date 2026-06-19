from django.views.generic import TemplateView
from apps.accounts.mixins import RoleRequiredMixin

from apps.custody.models import Inmate, SystemAlert

class OfficerDashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = ['PRISON_OFFICER', 'FACILITY_COMMANDER']
    template_name = 'custody/officer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determine the facility for the current user if they are a commander
        # Or just show global if PRISON_OFFICER (or simplify for now)
        base_qs = Inmate.objects.filter(is_active=True)
        
        context['total_in_custody'] = base_qs.count()
        context['pending_transfers'] = 0  # Placeholder as per current schema
        context['release_today'] = 0      # Placeholder as per current schema
        context['security_flags'] = SystemAlert.objects.filter(is_resolved=False).count()
        
        context['inmates'] = base_qs.select_related('facility')[:20] # limit to 20 for dashboard
        return context

class ManagementDashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = ['NCOS_MANAGEMENT']
    template_name = 'custody/management_dashboard.html'
