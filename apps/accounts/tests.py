from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from apps.accounts.models import User
from apps.accounts.services import get_dashboard_url_for_user
from apps.accounts.mixins import role_required, RoleRequiredMixin
from apps.accounts.views import LoginSuccessRedirectView

class AccountsServicesTests(TestCase):
    def setUp(self):
        self.clerk = User.objects.create_user(email='clerk@test.com', password='pwd', role='COURT_CLERK')
        self.officer = User.objects.create_user(email='officer@test.com', password='pwd', role='PRISON_OFFICER')
        self.commander = User.objects.create_user(email='commander@test.com', password='pwd', role='FACILITY_COMMANDER')
        self.mgmt = User.objects.create_user(email='mgmt@test.com', password='pwd', role='NCOS_MANAGEMENT')
        self.lawyer = User.objects.create_user(email='lawyer@test.com', password='pwd', role='LAWYER')
        self.unknown = User.objects.create_user(email='unknown@test.com', password='pwd', role='UNKNOWN')
        self.none_role = User.objects.create_user(email='none@test.com', password='pwd')
        self.superuser = User.objects.create_superuser(email='super@test.com', password='pwd')
        self.anonymous = AnonymousUser()

    def test_get_dashboard_url_for_user(self):
        self.assertEqual(get_dashboard_url_for_user(self.anonymous), 'two_factor:login')
        self.assertEqual(get_dashboard_url_for_user(self.superuser), 'accounts:superadmin_dashboard')
        self.assertEqual(get_dashboard_url_for_user(self.clerk), 'judiciary:clerk_dashboard')
        self.assertEqual(get_dashboard_url_for_user(self.officer), 'custody:officer_dashboard')
        self.assertEqual(get_dashboard_url_for_user(self.commander), 'custody:officer_dashboard')
        self.assertEqual(get_dashboard_url_for_user(self.mgmt), 'custody:management_dashboard')
        self.assertEqual(get_dashboard_url_for_user(self.lawyer), 'judiciary:lawyer_portal')
        self.assertEqual(get_dashboard_url_for_user(self.unknown), 'admin:index')
        self.assertEqual(get_dashboard_url_for_user(self.none_role), 'admin:index')


from django.views.generic import View

class DummyView(RoleRequiredMixin, View):
    allowed_roles = ['COURT_CLERK']
    def dispatch(self, request, *args, **kwargs):
        # Override to prevent calling super().dispatch which would call the actual view
        return super().dispatch(request, *args, **kwargs) or HttpResponse("OK")
    def get(self, request, *args, **kwargs):
        return HttpResponse("OK")

@role_required('LAWYER')
def dummy_decorator_view(request):
    return HttpResponse("OK")

class AccountsMixinsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.clerk = User.objects.create_user(email='clerk@test.com', password='pwd', role='COURT_CLERK')
        self.lawyer = User.objects.create_user(email='lawyer@test.com', password='pwd', role='LAWYER')
        self.anonymous = AnonymousUser()

    def test_role_required_mixin_allows_authorized(self):
        request = self.factory.get('/')
        request.user = self.clerk
        view = DummyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_role_required_mixin_denies_unauthorized(self):
        request = self.factory.get('/')
        request.user = self.lawyer
        view = DummyView.as_view()
        with self.assertRaises(PermissionDenied):
            view(request)

    def test_role_required_mixin_redirects_anonymous(self):
        request = self.factory.get('/')
        request.user = self.anonymous
        view = DummyView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('two_factor:login')))

    def test_role_required_decorator_allows_authorized(self):
        request = self.factory.get('/')
        request.user = self.lawyer
        response = dummy_decorator_view(request)
        self.assertEqual(response.status_code, 200)

    def test_role_required_decorator_denies_unauthorized(self):
        request = self.factory.get('/')
        request.user = self.clerk
        with self.assertRaises(PermissionDenied):
            dummy_decorator_view(request)

    def test_role_required_decorator_redirects_anonymous(self):
        request = self.factory.get('/')
        request.user = self.anonymous
        response = dummy_decorator_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('two_factor:login')))

class AccountsViewsTests(TestCase):
    def setUp(self):
        self.clerk = User.objects.create_user(email='clerk@test.com', password='pwd', role='COURT_CLERK')
        self.unknown = User.objects.create_user(email='unknown@test.com', password='pwd', role='UNKNOWN')

    def test_login_redirect_view_resolves(self):
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('accounts:login_redirect'))
        self.assertRedirects(response, reverse('judiciary:clerk_dashboard'), fetch_redirect_response=False)

    def test_login_redirect_view_fallback(self):
        self.client.force_login(self.unknown)
        response = self.client.get(reverse('accounts:login_redirect'))
        # Should fallback to admin:index
        self.assertRedirects(response, reverse('admin:index'), fetch_redirect_response=False)

    def test_logout_view(self):
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('two_factor:login'), fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', self.client.session)

from django.core import mail
from apps.accounts.forms import CustomUserCreationForm

class AccountsFormsTests(TestCase):
    def test_custom_user_creation_form_saves_and_emails(self):
        form_data = {'email': 'new_user@test.com', 'role': 'COURT_CLERK'}
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.email, 'new_user@test.com')
        self.assertEqual(user.role, 'COURT_CLERK')
        self.assertTrue(user.has_usable_password()) # password was generated and set
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Welcome to TRACE", mail.outbox[0].subject)
        self.assertIn(user.email, mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [user.email])

class AccountsSuperadminViewsTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(email='super@test.com', password='pwd')
        self.regular = User.objects.create_user(email='reg@test.com', password='pwd', role='LAWYER')

    def test_superadmin_dashboard_access_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('accounts:superadmin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/superadmin_dashboard.html')

    def test_superadmin_dashboard_denies_regular(self):
        self.client.force_login(self.regular)
        response = self.client.get(reverse('accounts:superadmin_dashboard'))
        self.assertEqual(response.status_code, 403)
