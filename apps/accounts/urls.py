from django.urls import path
from .views import LoginSuccessRedirectView, logout_view

app_name = 'accounts'

urlpatterns = [
    path('login-redirect/', LoginSuccessRedirectView.as_view(), name='login_redirect'),
    path('logout/', logout_view, name='logout'),
]
