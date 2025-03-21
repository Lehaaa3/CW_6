from django import template
import pycountry

from users.models import User

register = template.Library()


@register.simple_tag
def get_full_country_name(country_code):
    """
    get full country name
    :returns: full country name or country_code in case of error
    """
    try:
        full_country_name = pycountry.countries.get(alpha_2=str(country_code)).name
        return full_country_name
    except Exception as e:
        print(e)
        return country_code


@register.filter(name='check_is_manager')
def check_is_manager(user_id):
    """
    Check is user a manager
    :returns: Boolean value
    """
    user = User.objects.get(pk=user_id)
    if user.groups.filter(name='Managers'):
        return True
    else:
        return False