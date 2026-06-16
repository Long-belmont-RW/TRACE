from .models import User

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
