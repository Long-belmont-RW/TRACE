from datetime import timedelta
import logging
from django.utils import timezone
from django.db import transaction
from .models import Inmate, SystemAlert

logger = logging.getLogger(__name__)

def run_midnight_overdue_scan():
    """
    Scans for active inmates who haven't had a court update in 90 days.
    Flags them and creates a SystemAlert.
    """
    threshold_date = timezone.now().date() - timedelta(days=90)
    
    # Also considering inmates with NO last_court_update but admitted 90 days ago
    # For simplicity, we just check last_court_update for now as specified.
    active_inmates = Inmate.objects.filter(is_active=True)
    scanned_count = active_inmates.count()
    overdue_inmates = active_inmates.filter(
        has_overdue_flag=False,
        last_court_update__lte=threshold_date
    )
    flagged_count = overdue_inmates.count()
    
    with transaction.atomic():
        for inmate in overdue_inmates:
            inmate.has_overdue_flag = True
            inmate.save(update_fields=['has_overdue_flag'])
            
            SystemAlert.objects.create(
                inmate=inmate,
                alert_type='90_DAY_OVERDUE'
            )
    return {'scanned': scanned_count, 'flagged': flagged_count}

def escalate_alert_to_commander(alert_id, officer_user, note):
    alert = SystemAlert.objects.select_related('inmate__facility__commander').get(id=alert_id)
    alert.is_escalated = True
    alert.save(update_fields=['is_escalated', 'updated_at'])
    
    commander = alert.inmate.facility.commander
    if commander and commander.phone_number:
        logger.info(f"ALERT ESCALATED: Officer {officer_user.get_full_name() or officer_user.email} has escalated the 90-day flag for Inmate {alert.inmate.inmate_number}.")
