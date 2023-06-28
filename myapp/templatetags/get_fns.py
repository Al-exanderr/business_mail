from django import template
from myapp.models import Abonents



register = template.Library()

@register.simple_tag
def get_fns_verb(shpii):
    fns = Abonents.objects.filter(shpi = shpii)[:1]
    if fns.exists():
        fnss = Abonents.objects.get(shpi = shpii).fns_verbose
    else:
        fnss = 'запись не найдена'
    return fnss