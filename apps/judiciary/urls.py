from django.urls import path
from . import views

app_name = 'judiciary'

urlpatterns = [
    path('clerk-dashboard/', views.TodaysHearingsView.as_view(), name='clerk_dashboard'),
    path('log-decision/<int:case_id>/', views.LogDecisionView.as_view(), name='log_decision'),
    path('decision-success/', views.DecisionSuccessView.as_view(), name='decision_success'),
    path('decisions-log/', views.DecisionsLogView.as_view(), name='decisions_log'),
    path('lawyer-portal/', views.LawyerPortalView.as_view(), name='lawyer_portal'),
    path('timeline/<str:inmate_number>/', views.InmateTimelineView.as_view(), name='inmate_timeline'),
]
