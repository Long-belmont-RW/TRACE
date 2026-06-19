from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import RedirectView, TemplateView
from django.urls import reverse, NoReverseMatch
from .services import get_dashboard_url_for_user

from apps.custody.models import Facility
from django.contrib.auth import get_user_model
from django.contrib.admin.models import LogEntry

class SuperadminDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'accounts/superadmin_dashboard.html'

    def test_func(self):
        return self.request.user.is_superuser
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        
        context['total_institutions'] = Facility.objects.count()
        context['total_active_users'] = User.objects.filter(is_active=True).count()
        context['system_uptime'] = "99.99%"
        
        context['recent_logs'] = LogEntry.objects.select_related('user').order_by('-action_time')[:5]
        
        return context

class LoginSuccessRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        url_name = get_dashboard_url_for_user(self.request.user)
        try:
            return reverse(url_name)
        except NoReverseMatch:
            # Fallback since the target namespaces might not exist yet
            return reverse('admin:index')

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('two_factor:login')
