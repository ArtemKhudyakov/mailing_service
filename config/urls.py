from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('mailing_service/', include('mailing_service.urls', namespace='mailing_service')),
    path('users/', include('users.urls', namespace='users')),
]
