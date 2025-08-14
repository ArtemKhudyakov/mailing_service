from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, MailingAttempt
from datetime import datetime


def send_mailing(mailing_id):
    mailing = Mailing.objects.get(pk=mailing_id)

    for client in mailing.clients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=mailing,
                status='success',
                server_response='Email sent successfully'
            )
        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='failure',
                server_response=str(e)
            )

    # Обновляем статус рассылки, если время истекло
    if mailing.end_time <= datetime.now():
        mailing.status = 'completed'
        mailing.save()