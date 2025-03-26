from django import template

register = template.Library()


@register.simple_tag
def formatted_data(date_time_obj):
    """
    :returns datetime object in "%d.%m.%Y  %H:%M" format
    """

    return date_time_obj.strftime("%d.%m.%Y  %H:%M")


@register.filter()
def get_str_emails(clients_list):
    """
    :returns separate emails by html tag <br> as a string
    """

    str_emails = [client.email for client in clients_list if client.email]
    return "<br>".join(str_emails)
