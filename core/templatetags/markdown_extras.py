import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    html = md.markdown(
        text,
        extensions=['fenced_code', 'codehilite', 'tables', 'nl2br'],
    )
    return mark_safe(html)
