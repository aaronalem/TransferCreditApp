from django import template
from .. import views

register = template.Library()


@register.filter
def is_admin(user):
    return views.is_admin(user)
