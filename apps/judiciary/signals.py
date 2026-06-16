import django.dispatch

# Signal triggered when a new hearing log is created
hearing_log_created_signal = django.dispatch.Signal()
