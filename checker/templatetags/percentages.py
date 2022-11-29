from django import template

register = template.Library()

# this function will be used as a filter in django templates
# it returns the rounded result of a percentage calculation
@register.filter
def discount(value, percentage):
    result = round(value - (value * percentage / 100))
    return result