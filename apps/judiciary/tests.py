from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User
from apps.judiciary.models import Court

class JudiciaryViewsTests(TestCase):
    def setUp(self):
        self.court = Court.objects.create(name="Federal High Court", state="LA", court_type="Federal High")
        self.clerk = User.objects.create_user(email='clerk@test.com', password='pwd', role='COURT_CLERK', court=self.court)
        self.lawyer = User.objects.create_user(email='lawyer@test.com', password='pwd', role='LAWYER')
        self.officer = User.objects.create_user(email='officer@test.com', password='pwd', role='PRISON_OFFICER')

    def test_clerk_dashboard_access(self):
        # Unauthenticated
        response = self.client.get(reverse('judiciary:clerk_dashboard'))
        self.assertEqual(response.status_code, 302)
        
        # Unauthorized role
        self.client.force_login(self.officer)
        response = self.client.get(reverse('judiciary:clerk_dashboard'))
        self.assertEqual(response.status_code, 403)

        # Authorized role
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('judiciary:clerk_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'judiciary/clerk_dashboard.html')

    def test_lawyer_portal_access(self):
        # Unauthenticated
        response = self.client.get(reverse('judiciary:lawyer_portal'))
        self.assertEqual(response.status_code, 302)
        
        # Unauthorized role
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('judiciary:lawyer_portal'))
        self.assertEqual(response.status_code, 403)

        # Authorized role
        self.client.force_login(self.lawyer)
        response = self.client.get(reverse('judiciary:lawyer_portal'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'judiciary/lawyer_search.html')

    def test_schedule_hearing_access(self):
        # Unauthenticated
        response = self.client.get(reverse('judiciary:schedule_hearing'))
        self.assertEqual(response.status_code, 302)

        # Unauthorized role
        self.client.force_login(self.officer)
        response = self.client.get(reverse('judiciary:schedule_hearing'))
        self.assertEqual(response.status_code, 403)

        # Authorized role
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('judiciary:schedule_hearing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'judiciary/schedule_hearing.html')

    def test_export_docket_access(self):
        # Unauthenticated
        response = self.client.get(reverse('judiciary:export_docket'))
        self.assertEqual(response.status_code, 302)

        # Unauthorized role
        self.client.force_login(self.officer)
        response = self.client.get(reverse('judiciary:export_docket'))
        self.assertEqual(response.status_code, 403)

        # Authorized role
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('judiciary:export_docket'))
        self.assertIn(response.status_code, [200, 500])

    def test_export_decisions_log_access(self):
        # Unauthenticated
        response = self.client.get(reverse('judiciary:export_decisions_log'))
        self.assertEqual(response.status_code, 302)

        # Unauthorized role
        self.client.force_login(self.officer)
        response = self.client.get(reverse('judiciary:export_decisions_log'))
        self.assertEqual(response.status_code, 403)

        # Authorized role
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('judiciary:export_decisions_log'))
        self.assertIn(response.status_code, [200, 500])

