from django.db import models
from users.models import User

class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f"{self.full_name} ({self.email})"

class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.subject

class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Время начала')
    end_time = models.DateTimeField(verbose_name='Время окончания')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name='Статус'
    )
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    clients = models.ManyToManyField(Client, verbose_name='Клиенты')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-start_time']

    def __str__(self):
        return f"Рассылка {self.id} ({self.get_status_display()})"

class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failure', 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Время попытки')
    status = models.CharField(
        max_length=7,
        choices=STATUS_CHOICES,
        verbose_name='Статус попытки'
    )
    server_response = models.TextField(blank=True, verbose_name='Ответ сервера')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка')

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f"Попытка {self.id} ({self.get_status_display()})"