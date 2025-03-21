from django.forms import ModelForm

from distribution.models import Message, MailingSettings, Client


class StyleFormMixin:
    """
    Style Mixin for forms. Adds form-control attribute.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class MailingSettingsForm(StyleFormMixin, ModelForm):
    """
    Form for creating and updating mailing settings.

    Meta:
        model (MailingSettings): The model associated with this form.
        fields (tuple): The fields included in the form.

    Methods:
        __init__(self, args, *kwargs): Initializes the form and filters the
            'clients' and 'message' querysets based on the current user.
    """

    class Meta:
        model = MailingSettings
        fields = ('start_time', 'end_time', 'periodicity', 'status', 'clients', 'message')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['clients'].queryset = Client.objects.filter(owner=user)
            self.fields['message'].queryset = Message.objects.filter(owner=user)


class MessageForm(StyleFormMixin, ModelForm):
    """
    Form for creating and updating messages.

    Meta:
        model (MailingSettings): The model associated with this form.
        fields (tuple): The fields included in the form.
    """

    class Meta:
        model = Message
        fields = ('title', 'text',)


class ClientForm(StyleFormMixin, ModelForm):
    """
    Form for creating and updating clients.

    Meta:
        model (MailingSettings): The model associated with this form.
        fields (tuple): The fields included in the form.
    """

    class Meta:
        model = Client
        fields = ('FIO', 'email', 'comment',)
