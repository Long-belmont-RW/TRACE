from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User
from apps.custody.models import Facility

class CustodyViewsTests(TestCase):
    def setUp(self):
        self.facility = Facility.objects.create(name="Test Facility", state="LA")
        self.officer = User.objects.create_user(email='officer@test.com', password='pwd', role='PRISON_OFFICER', facility=self.facility)
        self.commander = User.objects.create_user(email='commander@test.com', password='pwd', role='FACILITY_COMMANDER', facility=self.facility)
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
        self.assertTemplateUsed(response, 'custody/ncos_dashboard.html')

        # Unauthorized role
        self.client.force_login(self.officer)
        response = self.client.get(reverse('custody:management_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_facility_inmates_view(self):
        self.client.force_login(self.officer)
        response = self.client.get(reverse('custody:facility_inmates'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custody/inmates_list.html')

    def test_facility_cases_view(self):
        self.client.force_login(self.officer)
        response = self.client.get(reverse('custody:facility_cases'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custody/cases_list.html')

    def test_statistical_cards_context(self):
        from apps.custody.models import Inmate, SystemAlert
        from django.utils import timezone
        import datetime
        inmate = Inmate.objects.create(
            inmate_number="INM-001",
            first_name="John",
            last_name="Doe",
            facility=self.facility,
            admission_date=datetime.date(2026, 1, 1)
        )
        alert1 = SystemAlert.objects.create(
            inmate=inmate,
            is_escalated=True
        )
        alert2 = SystemAlert.objects.create(
            inmate=inmate,
            is_resolved=True,
            date_resolved=timezone.now()
        )
        self.client.force_login(self.officer)
        response = self.client.get(reverse('custody:officer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recent_activity', response.context)
        self.assertIn('avg_resolution_days', response.context)
        self.assertEqual(len(response.context['recent_activity']), 2)

    def test_ncos_facility_directory_view(self):
        self.client.force_login(self.mgmt)
        response = self.client.get(reverse('custody:ncos_facility_directory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custody/ncos_facility_directory.html')

    def test_ncos_drilldown_views(self):
        self.client.force_login(self.mgmt)
        url_inmates = reverse('custody:ncos_facility_inmates', args=[self.facility.id])
        url_cases = reverse('custody:ncos_facility_cases', args=[self.facility.id])
        url_alerts = reverse('custody:ncos_facility_alerts', args=[self.facility.id])

        for url, tmpl in [(url_inmates, 'custody/ncos_facility_inmates.html'),
                          (url_cases, 'custody/ncos_facility_cases.html'),
                          (url_alerts, 'custody/ncos_facility_alerts.html')]:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200)
            self.assertTemplateUsed(res, tmpl)

    def test_ncos_global_search_view(self):
        self.client.force_login(self.mgmt)
        response = self.client.get(reverse('custody:ncos_global_search') + '?q=test')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'custody/ncos_global_search.html')

    def test_ncos_views_deny_unauthorized(self):
        self.client.force_login(self.clerk)
        response = self.client.get(reverse('custody:ncos_facility_directory'))
        self.assertEqual(response.status_code, 403)

    def test_trigger_midnight_scan_view(self):
        self.client.force_login(self.mgmt)
        response = self.client.get(reverse('custody:trigger_midnight_scan'))
        self.assertRedirects(response, reverse('custody:ncos_dashboard'))




