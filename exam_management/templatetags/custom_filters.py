from django import template
import json
from collections.abc import KeysView

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    return value.as_widget(attrs={'class': css_class})

@register.filter(name='jsonify')
def jsonify(object):
    if isinstance(object, dict):
        object = {key: list(value) if type(value) is KeysView else value for key, value in object.items()}
    try:
        return json.dumps(object)
    except TypeError as e:
        return str(e)

@register.filter(name='format_duration')
def format_duration(value):
    if not value:
        return ""
    total_seconds = int(value.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours} hours, {minutes} minutes" if hours else f"{minutes} minutes"