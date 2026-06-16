from django.dispatch import receiver
from apps.judiciary.signals import hearing_log_created_signal
from .models import Inmate

@receiver(hearing_log_created_signal)
def handle_hearing_log_created(sender, hearing_log, **kwargs):
    """
    When a HearingLog is created in judiciary, update the inmate's
    last_court_update and resolve 90-day overdue alerts.
    """
    case = hearing_log.case
    inmate = case.inmate
    
    # Update last_court_update
    inmate.last_court_update = hearing_log.hearing_date.date()
    inmate.has_overdue_flag = False
    inmate.save(update_fields=['last_court_update', 'has_overdue_flag'])
    
    # Resolve any 90-day active alerts
    alerts = inmate.alerts.filter(is_resolved=False, alert_type='90_DAY_OVERDUE')
    for alert in alerts:
        alert.is_resolved = True
        # Resolved by the system due to new hearing
        alert.save(update_fields=['is_resolved'])
