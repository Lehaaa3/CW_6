from django.db import models

from users.models import User

NULLABLE = {'null': True, 'blank': True}


class Client(models.Model):
    FIO = models.CharField(max_length=150, verbose_name='ФИО')
    email = models.EmailField(max_length=150, verbose_name='почта')
    comment = models.TextField(verbose_name='комментарий', **NULLABLE)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='владелец')

    def __str__(self):
        return f"{self.FIO} - {self.email}"

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"
        permissions = [
            ("can_see_all_clients", "Can see all clients"),
        ]


class Message(models.Model):
    title = models.CharField(max_length=100, verbose_name='тема письма')
    text = models.TextField(verbose_name='тело письма')


    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='владелец')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        permissions = [
            ("can_see_all_messages", "Can see all messages"),
        ]


class MailingSettings(models.Model):
    DAILY = "Раз в день"
    WEEKLY = "Раз в неделю"
    MONTHLY = "Раз в месяц"

    PERIODICITY_CHOICES = [
        (DAILY, "Раз в день"),
        (WEEKLY, "Раз в неделю"),
        (MONTHLY, "Раз в месяц"),
    ]

    CREATED = 'Создана'
    STARTED = 'Запущена'
    COMPLETED = 'Завершена'

    STATUS_CHOICES = [
        (COMPLETED, "Завершена"),
        (CREATED, "Создана"),
        (STARTED, "Запущена"),
    ]

    start_time = models.DateTimeField(verbose_name='время начала рассылки')
    end_time = models.DateTimeField(verbose_name='время окончания рассылки')
    periodicity = models.CharField(max_length=50, verbose_name='периодичность', choices=PERIODICITY_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=CREATED, verbose_name='статус рассылки')
    is_active = models.BooleanField(default=False, verbose_name='активность рассылки')

    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='сообщение', related_name='messages',
                                **NULLABLE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='владелец')
    clients = models.ManyToManyField(Client, verbose_name='клиенты рассылки', related_name='all_clients')

    def __str__(self):
        return f"Даты: {self.start_time.strftime('%d.%m.%Y')} - {self.end_time.strftime('%d.%m.%Y')}," \
               f" периодичность: {self.periodicity}," \
               f" статус: {self.status}"

    class Meta:
        verbose_name = 'настройки рассылки'
        verbose_name_plural = 'настройки рассылки'
        permissions = [
            ("can_see_all_mailing_settings", "Can see all mailing settings"),
        ]


class Log(models.Model):
    time = models.DateTimeField(verbose_name='дата и время последней попытки', auto_now_add=True)
    status = models.BooleanField(verbose_name='статус попытки')
    server_response = models.TextField(verbose_name='ответ почтового сервера', **NULLABLE)
    recipient = models.EmailField(verbose_name='email получателя', **NULLABLE)

    mailing_list = models.ForeignKey(MailingSettings, on_delete=models.CASCADE, verbose_name='рассылка')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='владелец')

    def __str__(self):
        return f'{self.time} {self.status}'

    class Meta:
        verbose_name = 'лог'
        verbose_name_plural = 'логи'
        permissions = [
            ("can_see_all_logs", "Can see all logs"),
        ]
        ordering = ['-time']
