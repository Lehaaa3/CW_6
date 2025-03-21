import logging
from django.db.models import Case, When, IntegerField

from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, UpdateView, FormView, TemplateView, ListView, DetailView

from distribution.tasks import stop_distribution_task
from users.models import User
from users.forms import UserRegisterForm, UserProfileForm, CustomAuthenticationForm, RestorePasswordForm, \
    SetNewPasswordForm
from users.services import send_greeting_email, send_verification_email, create_verification_code, \
    send_restore_password_email

logger = logging.getLogger(__name__)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')

    def post(self, request, *args, **kwargs):
        stop_distribution_task.delay(self.request.user.id)
        return super().post(request, *args, **kwargs)


class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('distribution:distribution_list')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['mailing_active'] = False

        return context_data


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.email_verification = create_verification_code()
        new_user.is_active = False
        verification_url = f'http://192.168.0.102:8000/users/activate/{new_user.email_verification}'
        email = form.cleaned_data.get('email')
        send_verification_email(verification_url, email)
        new_user.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('users:end_registration')


class ProfilerView(UpdateView):
    model = User
    form_class = UserProfileForm

    def get_success_url(self):
        return reverse('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.instance = self.request.user
        messages.success(self.request, 'Изменения успешно сохранены')
        return super().form_valid(form)


def activate(request, uid):
    try:
        user = User.objects.get(email_verification=uid)
        user.is_active = True
        fake_verification = create_verification_code()
        user.email_verification = fake_verification
        user.save()
        send_greeting_email(user.username, user.email)
        return redirect('users:email_activated')
    except Exception as e:
        logger.error(f"При попытке подтверждения почты произошла ошибка: {e}")
        return render(request, 'users/incorrect_link.html')


def email_activated(request):
    return render(request, "users/email_activated.html")


class EndRegistrationView(TemplateView):
    template_name = 'users/register_email_activation.html'

    def post(self, request):
        if request.method == 'POST':
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    user.email_verification = create_verification_code()
                    verification_url = f'http://127.0.0.1:8000/users/activate/{user.email_verification}'
                    send_verification_email(verification_url, email)
                    user.save()
                    return redirect(reverse('users:login'))
                else:
                    return redirect(reverse('users:email_activated'))
            except ObjectDoesNotExist:
                return HttpResponse(f"Пользователь с email: {email} не найден")


def restore_password(request):
    if request.method == "POST":
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                user.restore_password_verification = create_verification_code()
                restore_link = f'http://127.0.0.1:8000/users/restore_password/{user.restore_password_verification}'
                send_restore_password_email(restore_link, email)
                user.save()
                messages.success(request, f"Письмо для восстановления пароля отправлено на почту {email}")
                return redirect(reverse('users:login'))
            except ObjectDoesNotExist:
                form.add_error('email', "Пользователь с таким email не найден.")
                return render(request, "users/restore_password.html", {'form': form})

    else:
        form = RestorePasswordForm()
        return render(request, "users/restore_password.html", {'form': form})


def set_new_password(request, uid):
    if request.method == "POST":
        try:
            user = User.objects.get(restore_password_verification=uid)
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['password2']
                user.set_password(new_password)
                user.restore_password_verification = create_verification_code()
                user.save()
                messages.success(request, "Пароль успешно изменен. Вы можете войти в систему.")
                return redirect(reverse('users:login'))
            else:
                return render(request, 'users/set_new_password.html', {'form': form})

        except ObjectDoesNotExist:
            return HttpResponse(f"Произошла ошибка, запросите новую ссылку для восстановления пароля")

    else:
        try:
            user = User.objects.get(restore_password_verification=uid)
            form = SetNewPasswordForm()
            return render(request, 'users/set_new_password.html', {'form': form})
        except ObjectDoesNotExist:
            return render(request, 'users/incorrect_link.html')


class UserListView(ListView):
    model = User

    def get_queryset(self):
        return User.objects.all().order_by(
            Case(
                When(is_superuser=True, then=1),
                When(is_staff=True, then=2),
                When(is_blocked=False, then=3),
                default=4,
                output_field=IntegerField(),
            )
        )

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data()
        context_data['superusers'] = User.objects.filter(is_superuser=True).count()
        context_data['usual_users'] = User.objects.all().count() - User.objects.filter(is_staff=True).count()
        context_data['managers'] = User.objects.filter(groups__name='Managers').count()
        return context_data

    def post(self, request):
        if request.method == 'POST':
            object_id = request.POST.get('block_user')
            if object_id:
                user = User.objects.get(pk=object_id)
                user.is_blocked = True
                user.save()
            else:
                object_id = request.POST.get('unblock_user')
                if object_id:
                    user = User.objects.get(pk=object_id)
                    user.is_blocked = False
                    user.save()
            return redirect(reverse('users:user_list'))


@method_decorator(cache_page(60 * 3), name='dispatch')
class UsersDetailView(DetailView):
    model = User
