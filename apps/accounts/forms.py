from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.utils.crypto import get_random_string
from .models import User
from .services import send_onboarding_email

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        temp_password = get_random_string(length=12)
        user.set_password(temp_password)
        user._temp_password = temp_password
        if commit:
            user.save()
            send_onboarding_email(user, temp_password)
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'role', 'phone_number', 'bar_id', 'is_active', 'is_staff', 'is_superuser')
