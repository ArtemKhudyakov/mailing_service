from django.urls import path
from .views import (
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView,
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView,
    MailingListView, MailingCreateView, MailingUpdateView, MailingDeleteView,
    MailingDetailView, MailingStartView, MailingStatsView
)

app_name = 'mailing'

urlpatterns = [
    # Клиенты
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/add/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),

    # Сообщения
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/add/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    # Рассылки
    path('', MailingListView.as_view(), name='mailing_list'),
    path('add/', MailingCreateView.as_view(), name='mailing_create'),
    path('<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_update'),
    path('<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('<int:pk>/start/', MailingStartView.as_view(), name='mailing_start'),

    # Статистика
    path('stats/', MailingStatsView.as_view(), name='mailing_stats'),
]