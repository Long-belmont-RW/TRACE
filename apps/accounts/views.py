from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, RedirectView, TemplateView, UpdateView
from django.urls import reverse, reverse_lazy, NoReverseMatch
from django.contrib import messages
from django.db.models import Q
from .services import get_dashboard_url_for_user
from .mixins import RoleRequiredMixin
from .forms import SuperadminUserCreationForm

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

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    fields = ['first_name', 'last_name', 'phone_number']
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:user_profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            url_name = get_dashboard_url_for_user(self.request.user)
            context['dashboard_url'] = reverse(url_name)
        except Exception:
            context['dashboard_url'] = '/'
        return context

class SuperadminUserCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = get_user_model()
    form_class = SuperadminUserCreationForm
    template_name = 'accounts/superadmin_add_user.html'
    allowed_roles = ['SUPERADMIN']
    success_url = reverse_lazy('accounts:superadmin_users_list')

    def form_valid(self, form):
        messages.success(self.request, "User account created successfully.")
        return super().form_valid(form)

class SuperadminUsersListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = get_user_model()
    template_name = 'accounts/superadmin_users_list.html'
    context_object_name = 'users'
    allowed_roles = ['SUPERADMIN']

    def get_queryset(self):
        User = get_user_model()
        queryset = User.objects.all().order_by('-date_joined')
        q = self.request.GET.get('q', '').strip()
        role = self.request.GET.get('role', '').strip()
        if q:
            queryset = queryset.filter(
                Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
            )
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        context['q'] = self.request.GET.get('q', '')
        context['selected_role'] = self.request.GET.get('role', '')
        context['role_choices'] = User.ROLE_CHOICES
        return context

