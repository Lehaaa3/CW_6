from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from users.models import User
from django.utils.safestring import mark_safe


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom form for authentication.
    """
    username = forms.EmailField(
        label="Почта",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email',
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        :raises: custom error in case of invalid username or password.
        """
        super().__init__(request, *args, **kwargs)
        self.error_messages['invalid_login'] = (
            "Неверный email или пароль. Пожалуйста, проверьте свои учетные данные."
        )

    def clean_username(self):
        """
        :returns: username
        :raises: custom message in case of user with entered email is blocked or email was not confirmed.
        """
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.get(email=username)
            if not user.is_active:
                link = 'http://127.0.0.1:8000/users/end_registration'
                message = mark_safe(f"<a href='{link}'>Подтвердите ваш email</a>")
                raise forms.ValidationError(message)
            if user.is_blocked:
                message = "Вы были заблокированы в сервисе"
                raise forms.ValidationError(message)
        except ObjectDoesNotExist:
            return username
        return username


class UserRegisterForm(forms.ModelForm):
    """
    Custom user registration form.
    """
    password = forms.CharField(label="Пароль",
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}))

    def __init__(self, *args, **kwargs):
        """
        Set css attrs to registration fields.
        """
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        help_texts = {
            'username': None,
        }

    def clean_password2(self):
        """
        Checks passwords validity.
        :returns: password2
        """
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        """
        Saves hashed password to database.
        :param commit: True
        :returns: user
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for user profile page.
    """

    def __init__(self, *args, **kwargs):
        """
        Set css attrs to profile fields.
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите фамилию'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите номер телефона'
        })
        self.fields['avatar'].widget.attrs.update({
            'class': 'form-control avatar-custom', 
            'placeholder': 'Изменить'
        })

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'country', 'avatar',)
        help_texts = {
            'username': None,
        }


class RestorePasswordForm(forms.Form):
    """
    Form for user password restoring.
    """
    email = forms.EmailField(
        label="Почта",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'})
    )


class SetNewPasswordForm(forms.Form):
    """
    Form for setting new user password.
    """
    password = forms.CharField(label="Пароль",
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}))

    def clean(self):
        """
        Checks if entered passwords are the same.
        :returns: cleaned_data
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            self.add_error('password', "Пароли не совпадают")

        return cleaned_data
