from django import template

register = template.Library()

@register.filter
def discount(value, percentage):
    result = round(value - (value * percentage / 100))
    return result