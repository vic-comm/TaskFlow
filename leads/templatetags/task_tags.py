from django.template import Library
register = Library()

@register.filter
def widget_type(field):
    return field.field.widget.__class__.__name__.lower()
