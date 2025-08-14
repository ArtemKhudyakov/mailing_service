from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mailing/', include('mailing_service.urls', namespace='mailing')),
    path('users/', include('users.urls', namespace='users')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
