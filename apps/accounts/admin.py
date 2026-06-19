from django.contrib import admin, messages
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .services import send_onboarding_email

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('email', 'role', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'bar_id')
    list_filter = ('role', 'is_staff', 'is_superuser')
    ordering = ('email',)

    # Required for custom user models using email as username
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'bar_id', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role'),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        After saving a newly created user, send the onboarding email.

        Django admin calls form.save(commit=False), so the form's own
        `if commit:` block is never reached. We send the email here
        instead, after the user has been persisted to the database.
        The temporary password is stashed on the user object by
        CustomUserCreationForm.save() as `_temp_password`.
        """
        super().save_model(request, obj, form, change)
        if not change:
            temp_password = getattr(obj, '_temp_password', None)
            if temp_password:
                send_onboarding_email(obj, temp_password)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Override UserAdmin.response_add() to bypass its special password-field
        redirect logic. UserAdmin expects password1/password2 fields in the
        add form; since we auto-generate a temporary password, it skips the
        normal success message and redirects to the password change page.

        We fall back to the standard ModelAdmin.response_add() and add our
        own confirmation message about the onboarding email.
        """
        messages.success(
            request,
            f"User \"{obj.email}\" was added successfully. "
            f"An onboarding email with temporary credentials has been sent."
        )
        return ModelAdmin.response_add(self, request, obj, post_url_continue)

