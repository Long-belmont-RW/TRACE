from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User

class JudiciaryViewsTests(TestCase):
    def setUp(self):
        self.clerk = User.objects.create_user(email='clerk@test.com', password='pwd', role='COURT_CLERK')
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
        self.assertTemplateUsed(response, 'judiciary/lawyer_portal.html')
