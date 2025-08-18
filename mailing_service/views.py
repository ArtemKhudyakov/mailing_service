from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from .tasks import send_mailing

from users.mixins import UserAccessMixin

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class GreetingView(TemplateView):
    template_name = "greeting.html"  # Приветствие для неавторизованных


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"  # Главная для авторизованных

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["total_mailings"] = Mailing.objects.filter(owner=user).count()
        context["active_mailings"] = Mailing.objects.filter(owner=user, status="started").count()
        context["unique_clients"] = Client.objects.filter(owner=user).values("email").distinct().count()

        return context


# Клиенты
@method_decorator(cache_page(60 * 5), name='dispatch')
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"
    paginate_by = 10

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user).order_by("-id")


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Клиент успешно создан!")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Данные клиента обновлены!")
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Клиент успешно удален!")
        return super().form_valid(form)


# Сообщения
@method_decorator(cache_page(60 * 5), name='dispatch')
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"
    paginate_by = 10

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user).order_by("-id")


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Сообщение успешно создано!")
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Сообщение обновлено!")
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Сообщение удалено!")
        return super().form_valid(form)


# Рассылки
@method_decorator(cache_page(60 * 5), name='dispatch')
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.role == 'manager':
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "all")
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Передаем пользователя в форму
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Рассылка успешно создана!")
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserAccessMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Рассылка обновлена!")
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Рассылка удалена!")
        return super().form_valid(form)


@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object
        context["attempts"] = MailingAttempt.objects.filter(mailing=mailing).order_by("-attempt_time")
        context["clients_count"] = mailing.clients.count()
        return context


class MailingStartView(View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing.owner != request.user:
            raise PermissionDenied

        if mailing.status == "created":
            mailing.status = "started"
            mailing.save()

            # Запускаем отправку
            send_mailing(mailing.id)

            messages.success(request, "Рассылка успешно запущена!")
        else:
            messages.warning(request, "Рассылка уже была запущена ранее!")

        return redirect("mailing:mailing_detail", pk=pk)


# Статистика
@method_decorator(cache_page(60 * 30), name='dispatch')
class MailingStatsView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/mailing_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Общая статистика
        attempts = MailingAttempt.objects.filter(mailing__owner=user)
        context["attempts_count"] = attempts.count()
        context["success_count"] = attempts.filter(status="success").count()
        context["failure_count"] = attempts.filter(status="failure").count()

        # Последние 20 попыток
        context["attempts"] = attempts.select_related("mailing").order_by("-attempt_time")[:20]

        return context
