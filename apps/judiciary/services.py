from django.db import transaction
from .models import HearingLog, CourtCase
from .signals import hearing_log_created_signal

def process_new_hearing_log(case_id, clerk, form_data):
    """
    Creates a new hearing log for a case, updates the case status if needed, 
    and triggers the hearing_log_created_signal.
    All done within a database transaction.
    """
    with transaction.atomic():
        case = CourtCase.objects.get(id=case_id)
        
        hearing_log = HearingLog.objects.create(
            case=case,
            clerk=clerk,
            outcome=form_data['outcome'],
            bail_amount=form_data.get('bail_amount'),
            bail_conditions=form_data.get('bail_conditions'),
            notes=form_data.get('notes', '')
        )
        
        # Update case status if outcome is DISMISSED or SENTENCED
        if hearing_log.outcome == 'DISMISSED':
            case.status = 'DISMISSED'
            case.save(update_fields=['status'])
        elif hearing_log.outcome == 'SENTENCED':
            case.status = 'CONVICTED' # Mapping SENTENCED outcome to CONVICTED status
            case.save(update_fields=['status'])
        
        # Trigger signal for decoupled communication (e.g., for custody app)
        hearing_log_created_signal.send(sender=HearingLog, hearing_log=hearing_log)
        
        return hearing_log
