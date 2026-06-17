from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User

class CustodyViewsTests(TestCase):
    def setUp(self):
        self.officer = User.objects.create_user(email='officer@test.com', password='pwd', role='PRISON_OFFICER')
        self.commander = User.objects.create_user(email='commander@test.com', password='pwd', role='FACILITY_COMMANDER')
        self.mgmt = User.objects.create_user(email='mgmt@test.com', password='pwd', role='NCOS_MANAGEMENT')
        self.clerk = User.objects.create_user(email='clerk@test.com', password='pwd', role='COURT_CLERK')

    def test_officer_dashboard_access_officer(self):
        # Authorized role: PRISON_OFFICER
        self.client.force_login(self.officer)
        response = self.client.get(reverse('custody:officer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custody/officer_dashboard.html')

    def test_officer_dashboard_access_commander(self):
        # Authorized role: FACILITY_COMMANDER
        self.client.force_login(self.commander)
        response = self.client.get(reverse('custody:officer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custody/officer_dashboard.html')

    def test_officer_dashboard_denies_others(self):
        # Unauthorized role
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('custody:officer_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_management_dashboard_access(self):
        # Authorized role
        self.client.force_login(self.mgmt)
        response = self.client.get(reverse('custody:management_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custody/management_dashboard.html')

        # Unauthorized role
        self.client.force_login(self.officer)
        response = self.client.get(reverse('custody:management_dashboard'))
        self.assertEqual(response.status_code, 403)
