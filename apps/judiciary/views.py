import datetime
from django.views.generic import ListView, FormView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from apps.accounts.mixins import RoleRequiredMixin, role_required
from apps.custody.models import Inmate
from .models import CourtCase, HearingLog
from .forms import LogDecisionForm, ScheduleHearingForm
from . import services

class TodaysHearingsView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = CourtCase
    allowed_roles = ['COURT_CLERK']
    template_name = 'judiciary/clerk_dashboard.html'
    context_object_name = 'cases'

    def get_queryset(self):
        return CourtCase.objects.filter(
            court=self.request.user.court,
            next_court_date__contains=str(datetime.date.today())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today_cases = self.get_queryset()
        context['total_hearings'] = today_cases.count()
        
        # Calculate case statuses
        context['completed_hearings'] = today_cases.filter(status='CONVICTED').count() + today_cases.filter(status='DISMISSED').count()
        context['pending_hearings'] = today_cases.filter(status='ONGOING').count()
        
        # Adjourned based on today's logs
        context['adjourned_hearings'] = HearingLog.objects.filter(
            case__in=today_cases,
            outcome='ADJOURNED',
            hearing_date__contains=str(datetime.date.today())
        ).count()
        return context

class LogDecisionView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    template_name = 'judiciary/log_decision.html'
    form_class = LogDecisionForm
    allowed_roles = ['COURT_CLERK']
    success_url = reverse_lazy('judiciary:decision_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = get_object_or_404(CourtCase, id=self.kwargs['case_id'])
        return context

    def form_valid(self, form):
        services.process_new_hearing_log(
            case_id=self.kwargs['case_id'],
            clerk=self.request.user,
            form_data=form.cleaned_data
        )
        return super().form_valid(form)

class DecisionSuccessView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'judiciary/success.html'
    allowed_roles = ['COURT_CLERK']

class DecisionsLogView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = HearingLog
    allowed_roles = ['COURT_CLERK']
    template_name = 'judiciary/decisions_log.html'
    context_object_name = 'logs'

    def get_queryset(self):
        return HearingLog.objects.filter(case__court=self.request.user.court).order_by('-hearing_date')

class LawyerPortalView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = CourtCase
    allowed_roles = ['LAWYER']
    template_name = 'judiciary/lawyer_search.html'
    context_object_name = 'cases'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return CourtCase.objects.filter(
                Q(case_number__icontains=query) |
                Q(inmate__first_name__icontains=query) |
                Q(inmate__last_name__icontains=query)
            ).select_related('inmate', 'inmate__facility')
        return CourtCase.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        context['search_query'] = query

        cases = self.get_queryset()
        if query and cases.exists():
            case = cases.first()
            context['case_found'] = True
            context['case_details'] = {
                'inmate_name': f"{case.inmate.first_name} {case.inmate.last_name}",
                'case_number': case.case_number,
                'case_status': case.get_status_display().upper(),
                'custody_location': case.inmate.facility.name if case.inmate.facility else 'N/A',
                'next_court_date': case.next_court_date,
                'inmate_number': case.inmate.inmate_number,
            }
        else:
            context['case_found'] = False
        return context

class InmateTimelineView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'judiciary/timeline.html'
    allowed_roles = ['LAWYER']

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.GET.get('export') == 'pdf':
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
            rendered_html = render_to_string('judiciary/pdf_timeline_export.html', context, request=request)
            pdf_file = weasyprint.HTML(string=rendered_html).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            inmate_number = context['inmate'].inmate_number
            response['Content-Disposition'] = f'attachment; filename="timeline_{inmate_number}.pdf"'
            return response
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inmate_number = self.kwargs['inmate_number']
        inmate = get_object_or_404(Inmate, inmate_number=inmate_number)
        
        hearing_logs = HearingLog.objects.filter(
            case__inmate=inmate
        ).select_related('case').order_by('-hearing_date')
        
        context['inmate'] = inmate
        context['hearing_logs'] = hearing_logs
        return context


@method_decorator(role_required('COURT_CLERK'), name='dispatch')
class ScheduleHearingView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    template_name = 'judiciary/schedule_hearing.html'
    form_class = ScheduleHearingForm
    allowed_roles = ['COURT_CLERK']
    success_url = reverse_lazy('judiciary:clerk_dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['court'] = self.request.user.court
        return kwargs

    def form_valid(self, form):
        case = form.cleaned_data['case']
        case.next_court_date = form.cleaned_data['next_court_date']
        case.save()
        messages.success(self.request, "Hearing scheduled successfully.")
        return super().form_valid(form)


@method_decorator(role_required('COURT_CLERK'), name='dispatch')
class ClerkBatchExportView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['COURT_CLERK']

    def get(self, request, *args, **kwargs):
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

        cases = CourtCase.objects.filter(
            court=request.user.court,
            next_court_date__contains=str(datetime.date.today())
        ).select_related('inmate')
        
        context = {
            'cases': cases,
            'court': request.user.court,
            'today': datetime.date.today(),
        }
        rendered_html = render_to_string('judiciary/pdf_docket_export.html', context, request=request)
        pdf_file = weasyprint.HTML(string=rendered_html).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="daily_docket.pdf"'
        return response


class ClerkDecisionsExportView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['COURT_CLERK']

    def get(self, request, *args, **kwargs):
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

        logs = HearingLog.objects.filter(
            case__court=request.user.court
        ).select_related('case', 'case__inmate', 'clerk').order_by('-hearing_date')
        
        context = {
            'logs': logs,
            'court': request.user.court,
            'today': datetime.date.today(),
        }
        rendered_html = render_to_string('judiciary/pdf_decisions_export.html', context, request=request)
        pdf_file = weasyprint.HTML(string=rendered_html).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="decisions_log.pdf"'
        return response


