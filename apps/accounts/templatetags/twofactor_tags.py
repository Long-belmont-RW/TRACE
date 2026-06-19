from django import template
from django_otp.plugins.otp_totp.models import TOTPDevice

register = template.Library()


@register.simple_tag
def has_totp_device(user):
    """
    Check if the given user has a confirmed TOTP device set up.

    Usage in templates:
        {% load twofactor_tags %}
        {% has_totp_device user as has_2fa %}
        {% if has_2fa %}...{% endif %}
    """
    if not user.is_authenticated:
        return False
    return TOTPDevice.objects.filter(user=user, confirmed=True).exists()
