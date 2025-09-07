from django.template import Library
register = Library()

@register.filter
def completed_tasks(tasks):
    return tasks.filter(status='completed').count()

@register.filter
def count_tasks(tasks):
    return tasks.count()

@register.filter
def ratio(tasks):
    return (tasks.filter(status='completed').count()/tasks.count()) * 100