from django.db import transaction
from .models import HearingLog, CourtCase
from .signals import hearing_log_created_signal

def process_new_hearing_log(case_id, clerk, outcome, bail_amount=None, bail_conditions=None, notes=''):
    """
    Creates a new hearing log for a case and triggers the hearing_log_created_signal.
    All done within a database transaction.
    """
    with transaction.atomic():
        case = CourtCase.objects.get(id=case_id)
        
        hearing_log = HearingLog.objects.create(
            case=case,
            clerk=clerk,
            outcome=outcome,
            bail_amount=bail_amount,
            bail_conditions=bail_conditions,
            notes=notes
        )
        
        # Trigger signal for decoupled communication
        hearing_log_created_signal.send(sender=HearingLog, hearing_log=hearing_log)
        
        return hearing_log
