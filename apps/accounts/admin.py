from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'role', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('role', 'phone_number', 'bar_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role'),
        }),
    )
    search_fields = ['email', 'role']
    ordering = ['email']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and hasattr(obj, '_temp_password'):
            from .services import send_onboarding_email
            send_onboarding_email(obj, obj._temp_password)

admin.site.register(User, CustomUserAdmin)
