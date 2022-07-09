from django import template

register = template.Library()

@register.filter
def get_PRJ_ONLY(value,arg):
    x=value.split("_")
    return x[int(arg)]
