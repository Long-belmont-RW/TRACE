from .models import User

from django.core.mail import send_mail
from django.conf import settings

def get_users_by_role(role):
    """
    Returns all users with a specific role.
    """
    return User.objects.filter(role=role)

def get_dashboard_url_for_user(user):
    """
    Returns the appropriate dashboard URL namespace based on the user's role.
    """
    if not user.is_authenticated:
        return 'two_factor:login'

    if user.is_superuser or getattr(user, 'role', None) == 'SUPERADMIN':
        return 'accounts:superadmin_dashboard'

    role = getattr(user, 'role', None)

    if role == 'COURT_CLERK':
        return 'judiciary:clerk_dashboard'
    elif role in ['PRISON_OFFICER', 'FACILITY_COMMANDER']:
        return 'custody:officer_dashboard'
    elif role == 'NCOS_MANAGEMENT':
        return 'custody:management_dashboard'
    elif role == 'LAWYER':
        return 'judiciary:lawyer_portal'
    
    # Fallback if no matching role
    return 'admin:index'

def send_onboarding_email(user, temp_password):
    """
    Sends an onboarding email to a newly provisioned user with their temporary credentials.
    """
    subject = "Welcome to TRACE - Your Account Credentials"
    message = f"""
Hello,

Your account for the TRACE system has been successfully provisioned.
Your assigned role is: {user.role}

Here are your temporary login credentials:
Email: {user.email}
Temporary Password: {temp_password}

Please log in immediately and set up your Two-Factor Authentication.

Regards,
TRACE Administration
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@trace.test'),
        recipient_list=[user.email],
        fail_silently=False,
    )
