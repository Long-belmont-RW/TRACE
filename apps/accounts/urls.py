from django.urls import path
from .views import (
    LoginSuccessRedirectView,
    logout_view,
    SuperadminDashboardView,
    SuperadminUserCreateView,
    SuperadminUsersListView,
    UserProfileUpdateView,
)

app_name = 'accounts'

urlpatterns = [
    path('login-redirect/', LoginSuccessRedirectView.as_view(), name='login_redirect'),
    path('logout/', logout_view, name='logout'),
    path('superadmin-dashboard/', SuperadminDashboardView.as_view(), name='superadmin_dashboard'),
    path('superadmin/users/', SuperadminUsersListView.as_view(), name='superadmin_users_list'),
    path('superadmin/users/add/', SuperadminUserCreateView.as_view(), name='superadmin_add_user'),
    path('profile/', UserProfileUpdateView.as_view(), name='user_profile'),
]

