from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from .models import Inmate, SystemAlert

def run_midnight_overdue_scan():
    """
    Scans for active inmates who haven't had a court update in 90 days.
    Flags them and creates a SystemAlert.
    """
    threshold_date = timezone.now().date() - timedelta(days=90)
    
    # Also considering inmates with NO last_court_update but admitted 90 days ago
    # For simplicity, we just check last_court_update for now as specified.
    overdue_inmates = Inmate.objects.filter(
        is_active=True,
        has_overdue_flag=False,
        last_court_update__lte=threshold_date
    )
    
    with transaction.atomic():
        for inmate in overdue_inmates:
            inmate.has_overdue_flag = True
            inmate.save(update_fields=['has_overdue_flag'])
            
            SystemAlert.objects.create(
                inmate=inmate,
                alert_type='90_DAY_OVERDUE'
            )
    return overdue_inmates.count()
