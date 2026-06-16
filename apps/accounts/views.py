from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.urls import reverse, NoReverseMatch
from .services import get_dashboard_url_for_user

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
