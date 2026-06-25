from django.views.generic import TemplateView, View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.accounts.mixins import RoleRequiredMixin, role_required
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib import messages
from apps.custody.services import run_midnight_overdue_scan

import csv
from django.template.loader import render_to_string

from apps.custody.models import Inmate, SystemAlert, Facility
from apps.custody.services import escalate_alert_to_commander
from apps.judiciary.models import CourtCase
from django.db.models import Count, Q, Avg, ExpressionWrapper, F, DurationField
from django.utils import timezone
import datetime

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

class OfficerDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ['PRISON_OFFICER', 'FACILITY_COMMANDER']
    template_name = 'custody/officer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        facility = self.request.user.facility
        user_role = self.request.user.role
        
        base_alerts = SystemAlert.objects.filter(inmate__facility=facility, is_resolved=False)
        if user_role == 'PRISON_OFFICER':
            alerts = base_alerts.filter(is_escalated=False)
        elif user_role == 'FACILITY_COMMANDER':
            alerts = base_alerts.filter(is_escalated=True)
        else:
            alerts = base_alerts.none()
            
        context['alerts'] = alerts
        context['total_inmates'] = Inmate.objects.filter(facility=facility).count()
        context['active_alerts_count'] = alerts.count()
        context['user_role'] = user_role

        recent_activity = SystemAlert.objects.filter(
            inmate__facility=facility
        ).filter(
            Q(is_escalated=True) | Q(is_resolved=True)
        ).order_by('-updated_at')[:5]

        resolved_alerts = SystemAlert.objects.filter(
            inmate__facility=facility,
            is_resolved=True,
            date_resolved__isnull=False,
            date_flagged__isnull=False
        )
        agg_res = resolved_alerts.aggregate(
            avg_diff=Avg(
                ExpressionWrapper(
                    F('date_resolved') - F('date_flagged'),
                    output_field=DurationField()
                )
            )
        )
        avg_diff = agg_res.get('avg_diff')
        if avg_diff is None:
            avg_days = 0.0
        elif isinstance(avg_diff, datetime.timedelta):
            avg_days = float(avg_diff.total_seconds() / 86400.0)
        elif isinstance(avg_diff, (int, float)):
            avg_days = float(avg_diff / 86400000000.0)
        else:
            avg_days = 0.0

        context['recent_activity'] = recent_activity
        context['avg_resolution_days'] = avg_days
        
        return context

class EscalateAlertView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['PRISON_OFFICER']

    def post(self, request, *args, **kwargs):
        alert_id = request.POST.get('alert_id')
        note = request.POST.get('note', '')
        
        escalate_alert_to_commander(alert_id, request.user, note)
        messages.success(request, "Alert escalated successfully.")
            
        return HttpResponseRedirect(reverse('custody:officer_dashboard'))

class ResolveAlertView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['FACILITY_COMMANDER']

    def post(self, request, *args, **kwargs):
        alert_id = request.POST.get('alert_id')
        
        try:
            alert = SystemAlert.objects.get(id=alert_id, inmate__facility=request.user.facility)
            alert.is_resolved = True
            alert.resolved_by = request.user
            alert.date_resolved = timezone.now()
            alert.save()
            messages.success(request, "Alert marked as resolved.")
        except SystemAlert.DoesNotExist:
            messages.error(request, "Alert not found.")
            
        return HttpResponseRedirect(reverse('custody:officer_dashboard'))

class NcosDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ['NCOS_MANAGEMENT']
    template_name = 'custody/ncos_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Task 2: Macro-Level Aggregation
        total_inmates = Inmate.objects.filter(is_active=True).count()
        active_alerts = SystemAlert.objects.filter(is_resolved=False).count()
        
        if total_inmates > 0:
            compliance_rate = ((total_inmates - active_alerts) / total_inmates) * 100
        else:
            compliance_rate = 100.0
            
        context['total_inmates_macro'] = total_inmates
        context['active_alerts_macro'] = active_alerts
        context['compliance_rate'] = round(compliance_rate, 1)

        # Task 3: Facility-Level Annotation
        facilities = Facility.objects.select_related('commander').annotate(
            total_inmates=Count('inmates', filter=Q(inmates__is_active=True), distinct=True),
            active_alerts=Count('inmates__alerts', filter=Q(inmates__alerts__is_resolved=False), distinct=True)
        )
        context['facilities'] = facilities

        # Task 4: Secure Data Injection for Chart.js
        labels = [f.name for f in facilities]
        data = [f.active_alerts for f in facilities]
        
        context['chart_data'] = {
            'labels': labels,
            'data': data
        }

        return context

class FacilityReportsView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = ['PRISON_OFFICER', 'FACILITY_COMMANDER']
    template_name = 'custody/reports.html'

    def get(self, request, *args, **kwargs):
        facility = self.request.user.facility
        alerts = SystemAlert.objects.filter(inmate__facility=facility).order_by('-date_flagged')
        
        status = request.GET.get('status')
        if status == 'resolved':
            alerts = alerts.filter(is_resolved=True)
        elif status == 'escalated':
            alerts = alerts.filter(is_escalated=True)
            
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date and end_date:
            alerts = alerts.filter(date_flagged__range=[start_date, end_date + ' 23:59:59'])
            
        export = request.GET.get('export')
        if export == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="facility_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Date Flagged', 'Inmate Name', 'Inmate ID', 'Alert Type', 'Escalated Status', 'Resolved Status'])
            for alert in alerts:
                writer.writerow([
                    alert.date_flagged.strftime('%Y-%m-%d %H:%M'),
                    f"{alert.inmate.first_name} {alert.inmate.last_name}",
                    alert.inmate.inmate_number,
                    alert.alert_type,
                    'Yes' if alert.is_escalated else 'No',
                    'Yes' if alert.is_resolved else 'No'
                ])
            return response
            
        elif export == 'pdf':
            try:
                import weasyprint
            except (ImportError, OSError) as e:
                from django.http import HttpResponseServerError
                return HttpResponseServerError(
                    "PDF generation is currently unavailable because the required OS-level dependencies "
                    "(GTK3, Pango, Cairo) are not installed or not in the system PATH. <br><br>"
                    "Please install GTK3 for Windows to enable this feature.<br><br>"
                    f"Technical details: {e}"
                )

            context = {'alerts': alerts, 'facility': facility, 'start_date': start_date, 'end_date': end_date}
            rendered_html = render_to_string('custody/pdf_report.html', context, request=request)
            pdf_file = weasyprint.HTML(string=rendered_html).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="facility_report.pdf"'
            return response
            
        context = self.get_context_data(**kwargs)
        context['alerts'] = alerts
        context['current_status'] = status
        context['start_date'] = start_date
        context['end_date'] = end_date
        return self.render_to_response(context)


class FacilityInmatesView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = ['PRISON_OFFICER', 'FACILITY_COMMANDER']
    template_name = 'custody/inmates_list.html'
    context_object_name = 'inmates'

    def get_queryset(self):
        return Inmate.objects.filter(facility=self.request.user.facility).order_by('last_name')


class FacilityCasesView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    allowed_roles = ['PRISON_OFFICER', 'FACILITY_COMMANDER']
    template_name = 'custody/cases_list.html'
    context_object_name = 'cases'

    def get_queryset(self):
        queryset = CourtCase.objects.filter(inmate__facility=self.request.user.facility)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(case_number__icontains=q) |
                Q(inmate__first_name__icontains=q) |
                Q(inmate__last_name__icontains=q)
            )
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['status_choices'] = CourtCase.STATUS_CHOICES
        return context


@method_decorator(role_required('NCOS_MANAGEMENT', 'SUPERADMIN'), name='dispatch')
class NcosFacilityDirectoryView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Facility
    template_name = 'custody/ncos_facility_directory.html'
    context_object_name = 'facilities'
    allowed_roles = ['NCOS_MANAGEMENT', 'SUPERADMIN']

    def get_queryset(self):
        return Facility.objects.annotate(
            total_inmates=Count('inmates', filter=Q(inmates__is_active=True), distinct=True),
            active_alerts=Count('inmates__alerts', filter=Q(inmates__alerts__is_resolved=False), distinct=True)
        ).select_related('commander').order_by('name')


@method_decorator(role_required('NCOS_MANAGEMENT', 'SUPERADMIN'), name='dispatch')
class NcosFacilityInmatesView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Inmate
    template_name = 'custody/ncos_facility_inmates.html'
    context_object_name = 'inmates'
    allowed_roles = ['NCOS_MANAGEMENT', 'SUPERADMIN']

    def get_queryset(self):
        return Inmate.objects.filter(facility_id=self.kwargs['facility_id']).order_by('last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facility'] = get_object_or_404(Facility, pk=self.kwargs['facility_id'])
        return context


@method_decorator(role_required('NCOS_MANAGEMENT', 'SUPERADMIN'), name='dispatch')
class NcosFacilityCasesView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = CourtCase
    template_name = 'custody/ncos_facility_cases.html'
    context_object_name = 'cases'
    allowed_roles = ['NCOS_MANAGEMENT', 'SUPERADMIN']

    def get_queryset(self):
        return CourtCase.objects.filter(inmate__facility_id=self.kwargs['facility_id']).select_related('inmate', 'court').order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facility'] = get_object_or_404(Facility, pk=self.kwargs['facility_id'])
        return context


@method_decorator(role_required('NCOS_MANAGEMENT', 'SUPERADMIN'), name='dispatch')
class NcosFacilityAlertsView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = SystemAlert
    template_name = 'custody/ncos_facility_alerts.html'
    context_object_name = 'alerts'
    allowed_roles = ['NCOS_MANAGEMENT', 'SUPERADMIN']

    def get_queryset(self):
        return SystemAlert.objects.filter(inmate__facility_id=self.kwargs['facility_id']).select_related('inmate', 'resolved_by').order_by('-date_flagged')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facility'] = get_object_or_404(Facility, pk=self.kwargs['facility_id'])
        return context


@method_decorator(role_required('NCOS_MANAGEMENT', 'SUPERADMIN'), name='dispatch')
class NcosGlobalSearchView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Inmate
    template_name = 'custody/ncos_global_search.html'
    context_object_name = 'inmates'
    allowed_roles = ['NCOS_MANAGEMENT', 'SUPERADMIN']

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        return Inmate.objects.filter(
            Q(inmate_number__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).select_related('facility').order_by('last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


@method_decorator(role_required('NCOS_MANAGEMENT'), name='dispatch')
class TriggerMidnightScanView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['NCOS_MANAGEMENT']

    def get(self, request, *args, **kwargs):
        result = run_midnight_overdue_scan()
        messages.success(request, f"System scan complete. Scanned: {result.get('scanned', 0)}, Flagged: {result.get('flagged', 0)}.")
        return redirect('custody:ncos_dashboard')


class SuperadminFacilitiesListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Facility
    template_name = 'custody/superadmin_facilities_list.html'
    context_object_name = 'facilities'
    allowed_roles = ['SUPERADMIN']

    def get_queryset(self):
        return Facility.objects.annotate(
            staff_count=Count('assigned_officers', distinct=True),
            inmate_count=Count('inmates', filter=Q(inmates__is_active=True), distinct=True)
        ).select_related('commander').order_by('name')



