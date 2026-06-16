from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'role', 'phone_number', 'bar_id', 'is_active', 'is_staff', 'is_superuser')
