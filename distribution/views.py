import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Case, When, IntegerField
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from celery_app import app
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from distribution.forms import MessageForm, MailingSettingsForm, ClientForm
from distribution.models import Client, Message, MailingSettings, Log
from distribution.tasks import start_distribution_task, stop_distribution_task

logger = logging.getLogger(__name__)


class ClientListView(LoginRequiredMixin, ListView):
    """
    CBV to display all clients.
    """
    model = Client

    def get_queryset(self):
        """
        Order such to display clients of the current user at first, then others.
        If user hasn't permission 'distribution.can_see_all_clients' filters queryset.
        :returns: Ordered and filtered queryset
        """
        queryset = super().get_queryset()

        queryset = queryset.order_by(
            Case(
                When(owner=self.request.user, then=1),
                default=2,
                output_field=IntegerField(),
            )
        )

        if self.request.user.has_perm('distribution.can_see_all_clients'):
            return queryset
        else:
            queryset = queryset.filter(owner=self.request.user)
            return queryset

    def get_context_data(self, *args, **kwargs):
        """
        Set 'title' to context_data for use in template
        :returns: context_data
        """
        context_data = super().get_context_data()
        context_data['title'] = 'Клиенты'
        return context_data


@method_decorator(cache_page(60 * 3), name='dispatch')
class ClientDetailView(LoginRequiredMixin, DetailView):
    """
    CBV to display extended information about certain client.
    """
    model = Client


class ClientCreateView(CreateView):
    """
    CBV to create client.
    """
    model = Client
    form_class = ClientForm

    def form_valid(self, form):
        """
        Fill owner field of the client creation form with current user.
        :returns: super().form_valid(form)
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('distribution:client_list')


class ClientUpdateView(UpdateView):
    """
    CBV to update information of certain client.
    """
    model = Client
    form_class = ClientForm

    def get_success_url(self):
        """
        :returns: reverse to clients page
        """
        return reverse('distribution:client_list')


class ClientDeleteView(DeleteView):
    """
    CBV to delete certain client.
    """
    model = Client

    def get_success_url(self):
        """
        :returns: reverse to clients page
        """
        return reverse('distribution:client_list')


class MessageListView(LoginRequiredMixin, ListView):
    """
    CBV to display messages.
    """
    model = Message

    def get_queryset(self):
        """
        Order such to display messages of the current user at first, then others.
        If user hasn't permission 'distribution.can_see_all_messages' filters queryset.
        :returns: Ordered and filtered queryset
        """
        queryset = super().get_queryset()

        queryset = queryset.order_by(
            Case(
                When(owner=self.request.user, then=1),
                default=2,
                output_field=IntegerField(),
            )
        )

        if self.request.user.has_perm('distribution.can_see_all_messages'):
            return queryset
        return queryset.filter(owner=self.request.user)

    def get_context_data(self, *args, **kwargs):
        """
        Set 'title' to context_data for use in template.
        :returns: context_data
        """
        context_data = super().get_context_data()
        context_data['title'] = 'Сообщения'
        return context_data


@method_decorator(cache_page(60 * 3), name='dispatch')
class MessageDetailView(LoginRequiredMixin, DetailView):
    """
    CBV to view information about certain message.
    """
    model = Message


class MessageCreateView(CreateView):
    """
    CBV to create message.
    """
    model = Message
    form_class = MessageForm

    def form_valid(self, form):
        """
        Fill owner field of the message creation form with current user.
        :return: super().form_valid(form)
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        :returns: reverse to messages page
        """
        return reverse('distribution:message_list')


class MessageUpdateView(UpdateView):
    """
    CBV to update information about certain message.
    """
    model = Message
    form_class = MessageForm

    def get_success_url(self):
        """
        :returns: reverse to message page
        """
        return reverse('distribution:message_list')


class MessageDeleteView(DeleteView):
    """
    CBV to delete certain message.
    """
    model = Message

    def get_success_url(self):
        """
        :returns: reverse to message page
        """
        return reverse('distribution:message_list')


class MailingSettingsListView(LoginRequiredMixin, ListView):
    """
    CBV to display mailing settings.
    """
    model = MailingSettings

    def get_queryset(self):
        """
        Order such to display mailing settings of the current user at first, then others.
        If user hasn't permission 'distribution.can_see_all_messages' filters queryset.
        :returns: Ordered and filtered queryset
        """
        queryset = super().get_queryset()

        queryset = queryset.order_by(
            Case(
                When(owner=self.request.user, then=1),
                default=2,
                output_field=IntegerField(),
            )
        )

        if self.request.user.has_perm('distribution.can_see_all_mailing_settings'):
            return queryset
        return queryset.filter(owner=self.request.user)

    def get_context_data(self, *args, **kwargs):
        """
        Checks if the current user has permission 'distribution.can_see_all_mailing_settings'
        and if true set context_data accordingly to see general users statistic, else - only current user statistic.
        Also checks possibility for cache using instead sending requests to  database.
        :returns: context_data
        """
        context_data = super().get_context_data(*args, **kwargs)
        now = timezone.localtime(timezone.now())
        for data in context_data['object_list']:
            if data.end_time < now:
                data.status = MailingSettings.COMPLETED
                data.save()

        all_mailings = cache.get('all')
        active = cache.get('active')
        title = cache.get('title')
        clients_count = cache.get('clients_count')
        mailing_list = cache.get('mailing_list')

        if self.request.user.has_perm('distribution.can_see_all_mailing_settings'):
            if not all_mailings or not active or not title or not clients_count or not mailing_list:
                all_mailings = context_data['all'] = context_data['object_list'].count()
                active = context_data['active'] = context_data['object_list'].filter(
                    status=MailingSettings.STARTED).count()
                context_data['mailing_active'] = self.request.session.get('mailing_active', False)
                title = context_data['title'] = 'Рассылки'

                mailing_list = context_data['object_list'].prefetch_related('clients')
                clients = set()
                [[clients.add(client.email) for client in mailing.clients.all()] for mailing in mailing_list]
                clients_count = context_data['clients_count'] = len(clients)

                cache.set('all', all_mailings, 60 * 2)
                cache.set('active', active, 60 * 2)
                cache.set('title', title, 60 * 2)
                cache.set('clients_count', clients_count, 60 * 2)
                cache.set('mailing_list', mailing_list, 60 * 2)

            else:
                context_data['all'] = all_mailings
                context_data['active'] = active
                context_data['mailing_active'] = self.request.session.get('mailing_active', False)
                context_data['title'] = title
                clients = set()
                [[clients.add(client.email) for client in mailing.clients.all()] for mailing in mailing_list]
                context_data['clients_count'] = clients_count
        else:
            if not all_mailings or not active or not title or not clients_count or not mailing_list:
                all_mailings = context_data['all'] = context_data['object_list'].filter(
                    owner=self.request.user).count()
                active = context_data['active'] = context_data['object_list'].filter(status=MailingSettings.STARTED,
                                                                                     owner=self.request.user).count()
                context_data['mailing_active'] = self.request.session.get('mailing_active', False)
                title = context_data['title'] = 'Рассылки'

                mailing_list = context_data['object_list'].filter(owner=self.request.user).prefetch_related('clients')
                clients = set()
                [[clients.add(client.email) for client in mailing.clients.all()] for mailing in mailing_list]
                clients_count = context_data['clients_count'] = len(clients)

                cache.set('all', all_mailings, 60 * 2)
                cache.set('active', active, 60 * 2)
                cache.set('title', title, 60 * 2)
                cache.set('clients_count', clients_count, 60 * 2)
                cache.set('mailing_list', mailing_list, 60 * 2)

            else:
                context_data['all'] = all_mailings
                context_data['active'] = active
                context_data['mailing_active'] = self.request.session.get('mailing_active', False)
                context_data['title'] = title
                clients = set()
                [[clients.add(client.email) for client in mailing.clients.all()] for mailing in mailing_list]
                context_data['clients_count'] = clients_count
        return context_data

    def post(self, request):
        """
        Post handling. According to clicked button starts or stops start_distribution_task.
        :returns: reverse mailing settings page
        """
        if request.method == 'POST':
            user_id = request.user.id
            if 'start' in request.POST:
                start_distribution_task.delay(user_id)
                request.session['mailing_active'] = True
                return redirect(reverse('distribution:distribution_list'))
            elif 'end' in request.POST:
                request.session['mailing_active'] = False
                stop_distribution_task.delay(user_id)
                return redirect(reverse('distribution:distribution_list'))
            elif 'enable' in request.POST:
                now = timezone.localtime(timezone.now())
                object_pk = request.POST.get('object_pk')
                mailing = MailingSettings.objects.get(pk=object_pk)
                if mailing.start_time <= now <= mailing.end_time:
                    mailing.is_active = True
                    mailing.status = MailingSettings.STARTED
                    mailing.save()
                    return redirect(reverse('distribution:distribution_list'))
                else:
                    messages.info(request,
                                  f"Не удалось запустить рассылку так как сроки ее работы : {mailing.start_time} - {mailing.end_time}")
                    return redirect(reverse('distribution:distribution_list'))
            elif 'disable' in request.POST:
                object_pk = request.POST.get('object_pk')
                mailing = MailingSettings.objects.get(pk=object_pk)
                mailing.is_active = False
                mailing.status = MailingSettings.COMPLETED
                mailing.save()
                return redirect(reverse('distribution:distribution_list'))


@method_decorator(cache_page(60 * 3), name='dispatch')
class MailingSettingsDetailView(DetailView):
    """
    CBV to view information about certain mailing setting.
    """
    model = MailingSettings


class MailingSettingsCreateView(CreateView):
    """
    CBV to create mailing setting.
    """
    model = MailingSettings
    form_class = MailingSettingsForm

    def get_form_kwargs(self):
        """
        Set to kwargs['user'] current user to get it in MailingSettingsForm to filter querysets.
        :returns: kwargs
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Fill owner field of the mailing settings creation form with current user.
        :returns: super().form_valid(form)
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        :returns: reverse to mailing settings page
        """
        return reverse('distribution:distribution_list')


class MailingSettingsUpdateView(UpdateView):
    """
    CBV to update mailing settings.
    """
    model = MailingSettings
    form_class = MailingSettingsForm

    def get_form_kwargs(self):
        """
        Set to kwargs['user'] current user to get it in MailingSettingsForm to filter querysets.
        :returns: kwargs
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        """
        :returns: reverse to mailing settings page
        """
        return reverse('distribution:distribution_list')


class MailingSettingsDeleteView(DeleteView):
    """
    CBV to delete certain mailing settings.
    """
    model = MailingSettings

    def get_success_url(self):
        """
        :returns: reverse to mailing settings page
        """
        return reverse('distribution:distribution_list')


@method_decorator(cache_page(60 * 2), name='dispatch')
class LogListView(LoginRequiredMixin, ListView):
    """
    CBV to display logs.
    """
    model = Log

    def get_queryset(self):
        """
        Checks if current user has permission 'distribution.can_see_all_logs', and if true - switch logs between all
        logs and personal logs of the current staff user after clicking on appropriate button.
        :returns: queryset
        """
        queryset = super().get_queryset()
        show_my_logs = self.request.GET.get('show_my_logs', 'false') == 'true'

        if show_my_logs:
            return queryset.filter(owner=self.request.user)
        elif self.request.user.has_perm('distribution.can_see_all_logs'):
            return queryset
        else:
            return queryset.filter(owner=self.request.user)

    def get_context_data(self, *args, **kwargs):
        """
        Checks if current user has permission 'distribution.can_see_all_logs' and 'show_my_logs' state.
        According to results set appropriate context_data
        :returns: context_data
        """
        context_data = super().get_context_data(*args, **kwargs)
        show_my_logs = self.request.GET.get('show_my_logs', 'false')

        if self.request.user.has_perm('distribution.can_see_all_logs'):
            context_data['show_my_logs'] = show_my_logs
            context_data['all'] = context_data['object_list'].count()
            context_data['success'] = context_data['object_list'].count()
            context_data['error'] = context_data['object_list'].filter(status=False).count()
            if show_my_logs == "true":
                context_data['title'] = 'Мои логи '
            else:
                context_data['title'] = 'Логи'
        else:
            context_data['all'] = context_data['object_list'].filter(owner=self.request.user).count()
            context_data['success'] = context_data['object_list'].filter(status=True, owner=self.request.user).count()
            context_data['error'] = context_data['object_list'].filter(status=False, owner=self.request.user).count()
            context_data['title'] = 'Логи'
        return context_data
