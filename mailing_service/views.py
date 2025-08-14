from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView,
    DetailView, View, TemplateView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count

from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm


#Клиенты
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user).order_by('-id')


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Клиент успешно создан!')
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Данные клиента обновлены!')
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Клиент успешно удален!')
        return super().form_valid(form)


#Сообщения
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'
    paginate_by = 10

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user).order_by('-id')


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано!')
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение обновлено!')
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение удалено!')
        return super().form_valid(form)


#Рассылки
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'
    paginate_by = 5

    def get_queryset(self):
        queryset = Mailing.objects.filter(owner=self.request.user)

        status = self.request.GET.get('status')
        if status in ['created', 'started', 'completed']:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', 'all')
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем пользователя в форму
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка успешно создана!')
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка обновлена!')
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка удалена!')
        return super().form_valid(form)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object
        context['attempts'] = MailingAttempt.objects.filter(mailing=mailing).order_by('-attempt_time')
        context['clients_count'] = mailing.clients.count()
        return context


class MailingStartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        # Проверка владельца
        if mailing.owner != request.user:
            raise PermissionDenied

        if mailing.status == 'created':
            mailing.status = 'started'
            mailing.save()

            # Здесь должна быть логика запуска рассылки через Celery
            # Например: send_mailing_task.delay(mailing.id)

            messages.success(request, 'Рассылка успешно запущена!')
        else:
            messages.warning(request, 'Рассылка уже была запущена ранее!')

        return redirect('mailing:mailing_detail', pk=pk)


# Статистика
class MailingStatsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailing/mailing_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Общая статистика
        context['total_mailings'] = Mailing.objects.filter(owner=user).count()
        context['active_mailings'] = Mailing.objects.filter(owner=user, status='started').count()
        context['unique_clients'] = Client.objects.filter(owner=user).values('email').distinct().count()

        # Статистика по рассылкам
        mailings = Mailing.objects.filter(owner=user).annotate(
            attempts_count=Count('mailingattempt')
        ).order_by('-start_time')[:5]

        context['recent_mailings'] = mailings

        # Статистика по попыткам
        attempts = MailingAttempt.objects.filter(mailing__owner=user).select_related('mailing') \
                       .order_by('-attempt_time')[:10]

        context['recent_attempts'] = attempts

        return context