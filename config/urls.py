from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from mailing_service.views import GreetingView, HomeView

urlpatterns = [
    path('', GreetingView.as_view(), name='greeting'),
    path('home/', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('mailing/', include('mailing_service.urls', namespace='mailing')),
    path('users/', include('users.urls', namespace='users')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
