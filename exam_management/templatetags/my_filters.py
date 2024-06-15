from django import template

register = template.Library()

@register.filter
def alpha_filter(value):
    """Converts a number to its corresponding uppercase ASCII character (1 -> A, 2 -> B, etc.)."""
    return chr(64 + value)

@register.filter(name='sub')
def sub(value, arg):
    """Subtracts the arg from the value."""
    try:
        return value - arg
    except Exception as e:
        return 0  # or however you wish to handle the exception
