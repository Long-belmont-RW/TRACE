from django.contrib import admin
from django.urls import path, include
from two_factor.urls import urlpatterns as tf_urls
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('custody/', include('apps.custody.urls', namespace='custody')),
    path('judiciary/', include('apps.judiciary.urls', namespace='judiciary')),
    path('', include(tf_urls)),
    path('', RedirectView.as_view(pattern_name='accounts:login_redirect', permanent=False), name='root'),
]
