from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, MailingAttempt, Client
from datetime import datetime
from django.utils import timezone

def send_mailing(mailing_id):
    """Отправляет рассылку и фиксирует попытки."""
    mailing = Mailing.objects.get(pk=mailing_id)
    clients = mailing.clients.all()  # Получаем всех клиентов рассылки

    for client in clients:
        try:
            # Отправляем письмо
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email],
                fail_silently=False,  # Если False, то при ошибке будет исключение
            )

            # Фиксируем успешную попытку
            MailingAttempt.objects.create(
                mailing=mailing,
                status='success',
                server_response='Email sent successfully',
            )

        except Exception as e:
            # Фиксируем неудачную попытку
            MailingAttempt.objects.create(
                mailing=mailing,
                status='failure',
                server_response=str(e),  # Сохраняем текст ошибки
            )

    # Обновляем статус рассылки, если время истекло
    if mailing.end_time <= timezone.now():
        mailing.status = 'completed'
        mailing.save()