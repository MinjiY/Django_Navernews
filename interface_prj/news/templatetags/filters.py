from django import template

register = template.Library()

@register.filter()
def __zip(value,count):
    count = [1,2,3]
    return zip(value, count)