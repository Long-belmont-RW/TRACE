import datetime
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q
from apps.accounts.mixins import RoleRequiredMixin
from apps.custody.models import Inmate
from .models import CourtCase, HearingLog
from .forms import LogDecisionForm
from . import services

class TodaysHearingsView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = CourtCase
    allowed_roles = ['COURT_CLERK']
    template_name = 'judiciary/clerk_dashboard.html'
    context_object_name = 'cases'

    def get_queryset(self):
        return CourtCase.objects.filter(next_court_date=datetime.date.today())

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
            hearing_date__date=datetime.date.today()
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
        return HearingLog.objects.filter(clerk=self.request.user).order_by('-hearing_date')

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

